# Two-developer trial

Recruit two actual developers independently; use aliases `dev-01` and `dev-02`. Each tester should have a fresh session and complete the tasks before seeing the other's feedback. The owner must arrange hosted access or ask testers to run the repository locally. A private link alone will not grant access.

Use an endpoint credential intended for the trial and share it privately. Never give testers the owner's Hugging Face token or Modal account credentials. The current endpoint supports one application key, not independently revocable tester keys. Do not claim per-user isolation; coordinate the test and rotate the shared trial key afterward if appropriate, updating the owner's client as well.

## Tasks

1. Follow the README to run the app (or use access explicitly arranged by the owner).
2. Configure the agreed endpoint and click Check connection once.
3. Send one prompt of your own in a language you understand.
4. Run the four starter cases in Live endpoint mode.
5. Review one answer you can assess: add your own note and optional human score.
6. Export JSON and return it with the form below. Check that it contains no credentials or sensitive prompts.

Fixture-only trials are useful UI feedback but must be labelled fixture-only, not live integration tests. Do not assign a quality score in a language you cannot assess. Keep human feedback distinct from AI-generated observations.

## Copy this blank form for each tester

- Tester alias:
- Date and OS:
- Programming experience:
- Tested hosted site or local repository (commit):
- Live or fixture:
- Setup start time / first successful response time:
- Could finish independently? If not, what help was needed?
- Completed task numbers:
- Error encountered and reproduction steps:
- Most confusing step:
- Most useful feature:
- Would you use this for a project? Why or why not?
- One improvement:
- Permission to quote anonymized feedback in the submission: yes/no
- Export filename:

Do not fill this form on behalf of a tester or present two aliases as two people. Two trials provide early descriptive feedback, not broad validation.
