# Architecture Decision Record
An Architecture Decision Record is documentation that records important engineering decisions. By using Michael Nygard's ADR shape, for each decision I can explain why I made it, what alternatives were rejected and the consequences (both good and bad) that follow as a result of this decision. 

## ADR-0001 — Evaluate phishing detection using recall at a fixed false-positive rate

### Status
Accepted

### Context
Phishing detection is an imbalanced classification problem. In a realistic email stream, legitimate emails greatly outnumber phishing emails, which means that ordinary classification accuracy can give a misleading impression of model quality.

For example, if 99% of emails are legitimate, then a useless model that predicts every email as legitimate could achieve approximately 99% accuracy while detecting no phishing emails at all. Therefore, accuracy does not truly describe how well the system performs on the rare class that we actually need to detect.

Instead I use Recall because it measures the proportion of phishing emails that the model successfully identifies. However, maximising recall by itself is also insufficient. A model could achieve very high recall simply by flagging a large amount of legitimate mail as phishing. In a production email system this would disrupt users and reduce trust in the detector. 

We also opt for Recall, instead of Precison, because Recall penalises false negatives. In this case, the false negative of allowing a Phishing email to pass through the filter, is more costly to the business than a legitimate email being blocked (false positive). 

### Decision

I set the primary KPI to: **phishing recall at a false-positive rate of no more than 1%**. The model is therefore optimised and compared based on how much phishing it can detect while satisfying: **FPR ≤ 1%**

### Consequences

#### Improvements

Using recall at a fixed false-positive rate gives us a much more realistic way of judging whether the model is actually useful. A model cannot get a good result simply because most emails are legitimate. The 1% false-positive limit also prevents the model from increasing recall by just flagging more and more legitimate emails as phishing. As a result, we can now compare two different models under the same condition

#### Trade-offs
Recall at a fixed FPR is less immediately understandable than a single metric such as accuracy.

---

## ADR-0002 — Treat false-positive rate, review capacity, and latency as hard constraints

### Status
Accepted

### Context
A model may detect more phishing emails but also block too many legitimate emails. It could also send so many uncertain messages for the human review that the reviewer cannot keep up. Because of this, these requirements are actually limits that the system needs to stay within.

The Human review rate is especially important here because it is a limited resource. Without a fixed review budget, a model could appear to perform better simply by passing a large number of difficult cases to a human instead of making the decision itself.

Therefore, we need to establish clear limits that every candidate model must meet before it can be considered for deployment.

### Decision
I treat the following production requirements as **hard constraints**:
* **False-positive rate:** FPR ≤ 1%.
* **Human-review rate:** no more than 5% of messages are sent for review.
* **Prediction latency:** p95 inference latency remains below 500 ms.

A candidate model must satisfy all three constraints before improvements in detection performance are considered.  which will be evaluated automatically during the model retraining and evaluation process.

### Consequences

#### Improvements
- A model cannot be considered better simply because it catches more phishing if the improvement comes at the cost of blocking too much legitimate mail or overwhelming the review process. 

- Making the requirements explicit also gives experiments clear pass/fail criteria and the constraints can be checked automatically whenever a new candidate model is trained.

#### Trade-offs
- Setting hard constraints reduce the space of models that can be deployed. We now have a set feasible region. A model with substantially higher recall may still be rejected if it exceeds only one operational constraint.

- The limits themselves may also need to change in the future. If reviewer capacity increases, or the acceptable false-positive rate changes, the constraints would need to be reviewed rather than treated as permanent values.
---

## ADR-0003 — Separate model scores from the block and review threshold policy

### Status
Accepted

### Context
The phishing model produces a score that represents how likely an email is to be phishing. The score itself does not tell the system whether the email should be allowed, sent for review, or blocked.

One option would be to choose fixed score thresholds, for example blocking every email with a score above 0.8. The problem is that these numbers may stop meaning the same thing when the model is retrained.

Different models can produce very different score distributions. Even a new version of the same type of model may assign slightly different scores to the same kinds of emails. Because of this, a threshold that gives us a 1% false-positive rate today might produce a much higher or lower rate after retraining.

The same issue applies to the review threshold. If we keep the threshold fixed while the score distribution changes, we may end up sending far more or far fewer than 5% of emails for review.

For this reason, the model score and the decision about what to do with that score should be treated as separate parts of the system.

### Decision
The model outputs a score, rather than making the final allow, review, or block decision itself.

A separate policy layer contains two thresholds:
- The block threshold is chosen so that the false-positive rate on legitimate emails stays at or below 1%.
- The review threshold is chosen so that the number of emails sent for review stays within the 5% review budget.

These thresholds are fitted using held-out data that is representative of the type of traffic expected to be seen in production. Whenever the model is retrained, the thresholds are fitted again rather than reusing the old values. The model and its threshold policy are versioned, deployed and rolled back together.

The deployed unit is therefore: `(model, policy)`

### Consequences
#### Improvements
- Retraining the model does not automatically change how aggressively the system blocks or reviews emails. Instead, the thresholds are adjusted to match the score distribution of the new model while still respecting the same production limits.

- This makes the system a lot more flexible. For example, the business can change the operational policy, such as the review budget without necessarily having to retrain the classifier itself, since simply the width of the review threshold would be increased

#### Trade-offs
- The main downside is that there is now another part of the system to maintain. The policy thresholds need to be fitted, tested, stored, and versioned alongside the model.

- We also need a representative held-out dataset to fit the thresholds properly. If this data does not reflect real production traffic, the thresholds may not behave as expected once deployed.

---

## ADR-0004 — Promote models only when all constraints pass and the primary objective improves

### Status
Accepted

### Context
The system is designed to retrain models regularly, so I need a consistent way of deciding whether a newly trained model should replace the current one.

### Decision
A candidate model is promoted only when all required checks pass and it improves at least one of the objectives we care about.

The required checks are:
1. FPR remains at or below 1%.
2. Human-review usage remains at or below 5%.
3. p95 latency remains below 500 ms.
4. The model does not perform worse on the novel-campaign evaluation tests.

Once these checks have passed, the candidate must improve at least one of the following:
- phishing recall at the required FPR
- adaptation speed
- label efficiency

### Consequences

#### Improvements
- We now have a consistent and reproducible way of deciding whether a model is actually an improvement

- It also makes automated retraining safer because the promotion rules are written down in advance, so a candidate can be evaluated in the same way every time

- The multiple rules also allows models to improve in different ways. For example, a new model may not greatly increase recall but could still be useful if it adapts to new campaigns faster or achieves similar performance using fewer labelled examples.

#### Trade-offs
- The main trade-off is that some models with useful improvements will still be rejected if they cause a regression somewhere else. For example, a candidate with higher recall may fail promotion because it performs worse on novel phishing campaigns or exceeds the latency requirement.
- The overall space of models is limited to a feasible region

---
