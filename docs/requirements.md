# Requirements - Self Adapting Email Phishing Detector
<!--- This requirements document is split into functional and non-functional requirements
I have strived to implement this as close to real-life production requirements -->

## Scope 
A closed-loop MLOps email filter that classifies **raw email text** and outputs `P(phishing)` with a confidence value. Confident cases are auto-decided (block / allow), while uncertain cases go to a **human review queue** ordered by how useful they would be / **learning entropy** (active learning). Human labels flow back into the database and, once enough accumulate (or drift/a new campaign is detected) the system **automatically triggers a retrain**. The candidate is **gated against hard constraints** (recall, FPR, review budget, latency), **A/B-tested** against the current model, and **promoted or rolled back automatically**. When a **novel campaign** appears — a new *"kind"* of attack the model has never seen — the system detects the degradation, a human labels a small, smartly chosen subset and the model recovers.

## Context
Phishing attacks are constantly evolving. A static detection model decays in reality, and manually retraining and building new models is not feasible. Therefore, a system that detects its own degradation, optimises the number of labels needed to re-achieve its detection capabilities and adapt to new attacks, with little human-intervention is very much needed

## Primary Objective and Metrics

The primary classification objective is to: **Maximise phishing recall subject to a bounded false-positive rate.**

The main classification result **MUST** therefore be reported as: **Recall at FPR ≤ 1%** rather than unconstrained accuracy or F1.

- PR-AUC and ROC-AUC **SHOULD** be reported as supporting summary metrics.

- Accuracy and F1 **COULD** be used for diagnosis and comparison, but they **MUST NOT** independently authorise deployment.

- The main adaptation KPI is **label efficiency**: how many fewer human labels are required using active learning than random sampling to recover from a novel phishing campaign.

The completed system **SHOULD** also report:
- labels-to-recover: the number of human-labelled emails required before the system restores at least 90% detection of a novel campaign while staying within the FPR and review limits.
- emails/time-to-adapt: the number of emails processed, or amount of elapsed time, between the start of a new campaign and successful model recovery.
- campaign-detection delay: the number of emails processed, or amount of time, between the start of a novel campaign and the system first detecting it as unusual behaviour.
- retrain precision: the proportion of triggered retraining runs that produce a candidate which passes the deployment gate and is suitable for deployment.
- post-promotion regression rate: the proportion of promoted models that later show unacceptable performance regression and require rollback.

---

## Functional Requirements
<!-- Define **WHAT** specific features and operations a system must perform to meet business needs and define the edge cases or special scenarios the system should handle. Opted to supplement inital descriptions with MoSCoW notation-->
- **FR-001**: The system **MUST** accept raw email text and produce a phishing score with a confidence value.
- **FR-002**: The system **MUST** use a separate decision policy to convert the phishing score from **FR-001** into three possible actions: {`ALLOW`, `REVIEW`, or `BLOCK`}
- **FR-003**: Decision thresholds **MUST** be fitted from evaluation data rather than permanently hardcoded into the classifier.
- **FR-004**: The system **MUST** provide a subset of low-confidence/uncertain emails to a human `Review Queue`
- **FR-005**: Reviewer-provided labels **MUST** be stored so that they can later be used for evaluation or retraining.
- **FR-006**: The system **MUST** prioritise useful training examples using active learning, when more review candidates exist than the available human-review capacity
- **FR-007**: The project **MUST** compare active-learning selection with random sampling
- **FR-008**: The system **MUST** be capable of triggering retraining when at least one of the following occurs:
    1. Enough new human labels have accumulated
    2. Model performance has degraded
    3. Significant drift has been detected
    4. A possible novel phishing campaign has been detected
- **FR-009**: Only one retraining process from **FR-008** must be allowed to run at a time
- **FR-010**: The system **MUST** be capable of detecting distribution drift and identifying groups of similar low-confidence emails that may represent a forming phishing campaign
- **FR-011**: A drift or campaign signal **MUST NOT** automatically be treated as a phishing label as human ground-truth labels are still required for supervised retraining
- **FR-012**: Every candidate model `(model, policy)` **MUST** pass the project's deployment gate before replacing the current production version. A candidate that violates a hard operational constraint **MUST** be rejected, regardless of improvements in other metrics
- **FR-013**: The system **SHOULD** support rollback to a previously valid `(model, policy)` if a promoted candidate later proves unsuitable
- **FR-014**: The system **SHOULD** record enough information to identify which model and policy produced a particular prediction or deployment decision.
- **FR-015**: The system **MUST** expose an API that accepts raw email content and returns the model score and resulting decision
- **FR-016**: The API **SHOULD** expose health and readiness information so that a running service can be distinguished from one that is actually ready to perform inference.
- **FR-017**: The system **MUST** provide a simple interface where a reviewer can inspect uncertain emails and assign labels.
- **FR-018**: The review interface **MUST** display emails according to the active-learning ordering when that functionality is available
- **FR-019**: The system **SHOULD** provide a dashboard showing the main health and adaptation metrics of the pipeline and **SHOULD** include information such as prediction volume, review rate, false-positive behaviour, latency, drift signals, retraining history, and campaign recovery.
- **FR-020**: The system **COULD** provide notifications for important events such as significant drift, failed retraining, candidate rejection, promotion, or rollback.
- **FR-021**: Routine retraining, policy fitting, evaluation, and promotion decisions **WON'T** depend on a developer manually choosing whichever model appears best.

## Non-Functional Requirements
<!-- Define **HOW** the system should operate, considering the following:
Perfomance - Speed and responsiveness; Security; Usability; Reliability; Scalability; Portability; Maintainability -->
- **NFR-001**: The system **MUST** maintain an automatic-blocking false-positive rate of: **FPR ≤ 1% by default** when evaluated on a production-representative dataset
- **NFR-002**: The system **MUST** keep the human-review rate at: **≤ 5% of inbound emails**
- **NFR-003**: The system **SHOULD** achieve **p95 single-email inference latency < 500 ms**
- **NFR-004**: Important experiment settings and dataset versions **MUST** be recorded so that a previous result can be understood and reproduced
- **NFR-005**: The system **MUST NOT** have hardcoded values/thresholds/paths/hyperparameters in validated config.
- **NFR-006**  The system **SHOULD** have structured (JSON) logging with correlation IDs
- **NFR-007** The system **SHOULD** have a leakage guard, treating an evaluation Phishing precision score of > 98% as a suspected leak, rather than a viable model


