"""Deploy from this folder: python -m modal deploy modal_app.py"""
import modal

MODEL_ID = "NCAIR1/N-ATLaS"
MODEL_REVISION = "e294476928aca9030e924ca27bb8e085e8581273"
app = modal.App("atlaslaunch-natlas")
cache = modal.Volume.from_name("atlaslaunch-model-cache", create_if_missing=True)
credentials = modal.Secret.from_name("atlaslaunch-secrets")

gpu_image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install(
        "torch==2.11.0", "transformers==5.19.0", "bitsandbytes==0.50.2",
        "accelerate==1.15.0", "huggingface_hub==1.33.0",
    )
    .env({"HF_HOME": "/model-cache", "HF_HUB_DISABLE_TELEMETRY": "1"})
)
web_image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install("fastapi==0.143.0")
    .add_local_python_source("atlas_modal_api")
)


@app.cls(
    image=gpu_image, gpu="T4", cpu=2, memory=16384,
    secrets=[credentials], volumes={"/model-cache": cache},
    min_containers=0, max_containers=1, scaledown_window=60,
    timeout=300, startup_timeout=900,
)
class Natlas:
    @modal.enter()
    def load(self):
        import os
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        options = dict(revision=MODEL_REVISION, token=os.environ["HF_TOKEN"],
                       trust_remote_code=False)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, **options)
        quantization = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, **options, quantization_config=quantization,
            device_map={"": 0}, dtype=torch.float16, use_safetensors=True,
        )
        self.model.eval()
        cache.commit()

    @modal.method()
    def generate(self, body: dict):
        import time
        import uuid
        from datetime import datetime, timezone
        import torch

        prompt = self.tokenizer.apply_chat_template(
            body["messages"], tokenize=False, add_generation_prompt=True,
            date_string=datetime.now(timezone.utc).strftime("%d %b %Y"),
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        input_count = inputs["input_ids"].shape[1]
        if input_count > 2048:
            return {"error": "context_limit"}
        inputs = inputs.to("cuda")
        options = {"max_new_tokens": body["max_tokens"],
                   "do_sample": body["temperature"] > 0,
                   "pad_token_id": self.tokenizer.eos_token_id}
        if options["do_sample"]:
            options["temperature"] = body["temperature"]
        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            output = self.model.generate(**inputs, **options)
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        tokens = output[0, input_count:]
        answer = self.tokenizer.decode(tokens, skip_special_tokens=True)
        eos = self.model.generation_config.eos_token_id
        eos_ids = eos if isinstance(eos, list) else [eos]
        stopped = bool(len(tokens) and int(tokens[-1]) in eos_ids)
        return {
            "id": "chatcmpl-" + uuid.uuid4().hex,
            "object": "chat.completion", "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": answer},
                         "finish_reason": "stop" if stopped else "length"}],
            "usage": {"prompt_tokens": input_count, "completion_tokens": len(tokens),
                      "total_tokens": input_count + len(tokens)},
            "atlaslaunch": {"model_revision": MODEL_REVISION, "quantization": "4-bit NF4",
                            "generation_seconds": elapsed},
        }


@app.function(image=web_image, secrets=[credentials], min_containers=0,
              max_containers=2, scaledown_window=30, timeout=900)
@modal.asgi_app()
def web():
    import os
    from atlas_modal_api import create_api
    return create_api(Natlas().generate.remote.aio, os.environ["ATLAS_API_KEY"])
