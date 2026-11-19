# machine-learning-fundamentals: supervised learning on tables, with results that hold up in use
kind: skill
aliases: machine learning, ml, scikit-learn, supervised learning, data leakage
needs: python-core
status: reviewed 2026-11-19 by independent agent, every Show rerun
sources: scikit-learn.org/stable: user_guide (coverage), common_pitfalls, cross_validation,
  classification_threshold, calibration, permutation_importance, model_persistence;
  Google ML Crash Course outline (order); Google Rules of ML (rules named); ISLP contents;
  reproducible.cs.princeton.edu (leakage kinds); arxiv.org/abs/2207.08815 (trees on tables); every pitfall run here
unverified: step order 11-13 and the depth each needs are judgement

## Promise
Turn labelled tabular data into a model that beats an honest baseline, measured so the number holds in use, with a plan for what to log and watch.

## The one idea
A model is judged only on examples it has never seen, chosen the way the future will arrive. Picture: an exam set by someone else; a student who saw the paper scores well and knows nothing. Where it breaks: the future may not look like any past sample (drift), so even a clean exam goes stale.

## In production
- On mid-sized tables, tree ensembles are the models to beat (Grinsztajn et al. 2022); images, text, audio call for neural networks.

## Teaching order
1. The question: one row per what, the label, the decision a prediction feeds; when a rule or a query would do (Rules of ML 1, 3); each error's cost and who bears it; may this data be used for this purpose.
2. The data in pandas: `read_csv`, `info()`, `describe()`, `value_counts()`, `isna().sum()`, `duplicated()`, `groupby`; raw rows read by eye; ids are not features; who set the label and when it becomes known.
3. The split: `train_test_split` with `stratify`; training, validation and test sets; duplicates kept to one side; a group on one side (`GroupShuffleSplit`); time order kept for forecasts.
4. A baseline before any model: the `fit`, `predict`, `score` interface on `DummyClassifier`, `DummyRegressor`; a one-line rule; the current system: the bar.
5. Linear regression: a weighted sum plus intercept; squared-error loss; gradient descent as walking downhill, the learning rate; a coefficient's meaning, changed by scale and correlated features; MAE, RMSE, R².
6. Logistic regression: the sigmoid turns a sum into a probability; log loss; `predict_proba` against `predict`; coefficients as log-odds; `calibration_curve`, `CalibratedClassifierCV`.
7. Preprocessing inside the model: `SimpleImputer`, `StandardScaler`, `OneHotEncoder(handle_unknown="ignore")` in a `ColumnTransformer` in a `Pipeline`, fitted on training rows only, the same object predicting.
8. Overfitting: training against validation score; a full-depth `DecisionTreeClassifier` memorising random labels; bias and variance; `learning_curve`, `validation_curve`; regularisation: `Ridge`, `Lasso`, `C`, `max_depth`.
9. Measuring classifiers: the confusion matrix; precision, recall, F1; ROC AUC against average precision; the 0.5 threshold replaced by one from error costs, chosen on validation data; rare classes: `class_weight`, never rows copied before a split.
10. Cross-validation and tuning: `cross_val_score`, `StratifiedKFold`, `GroupKFold`, `TimeSeriesSplit`; `GridSearchCV`, `RandomizedSearchCV` around the whole pipeline; one final test score.
11. Trees and ensembles: a split makes each side purer, depth the knob; `RandomForestClassifier` (bagging); `HistGradientBoostingClassifier` (learning rate, early stopping, missing values); `permutation_importance` on held-out rows.
12. Error analysis: wrong predictions read, most confident first; metrics per segment and per affected group; label errors and too-good features; fixes as features or data (Rules of ML 26).
13. The model in use: the whole pipeline in `joblib.dump`, loaded only from a trusted file, same library versions; serving inputs logged (training-serving skew, Rules of ML 29); input and prediction distributions watched; delayed labels; data and concept drift; a retrained model tested on later data against the live one.

## Judged by
- [3,10] The test set was scored once, after every choice was made.
- [2,12] No feature is known only after the moment of prediction, or derived from the label.
- [3] No duplicate and no person, device or session sits on both sides of a split; a model of the future is tested on later data.
- [7,10] Every fitted step (imputing, scaling, encoding, selecting) is inside the pipeline refitted per fold.
- [4] A baseline's score stands beside the model's.
- [1,9] The metric and threshold match the decision's costs; rare classes get precision and recall, not accuracy.
- [10] The spread across folds and seeds is stated.
- [1,12] The data's use was cleared; errors were compared across the groups the decision affects.
- [13] What is logged, watched and retrained, and when, is written before launch.

## Step notes
### 1
Need: My manager wants "an AI that predicts churn"; what do I build first, and how will I know it works?
Show: 2,000 rows, about 12% positive (`make_classification`, `weights=[0.9]`, `flip_y=0.05`), half held out. A
forest: 1.00 on its training rows, 0.88 to 0.95 held out; always "no" 0.88 to 0.89; the best one-column cut 0.85
to 0.91. Costed (a miss 50, an alarm 5): the forest won on accuracy in all 15 seeds run, on cost in 11; twice a
cut LESS accurate than always "no" was cheapest.
Explain: A model guesses about unseen rows, so it is scored on held-out rows, against the cheapest rival, in
what the decision pays; accuracy and cost can rank models differently.
Try: decide: their row, label, when it is known, each error's cost; predict: their training and held-out score.
### 2
Need: I fed my CSV to a model and got AUC 1.00 first try; was I lucky?
Show: 2,000 rows of noise features, 20% churned at random; the export sorted by outcome, then numbered
`customer_id`. A forest on a shuffled 30% held out: with the id AUC 1.000; without, 0.41 to 0.55.
`df.groupby(pd.qcut(df.customer_id, 5)).churned.mean()`: 0, 0, 0, 0 to 0.14, 0.93 to 1.
Explain: A column can carry the label through how the file was made; the label rate grouped by each column finds it.
Try: apply: on their table, `isna().sum()`, `duplicated().sum()`, the label rate by column fifths;
explain: who sets each column, and when.
### 3
Need: My test score said 97%; why is the model a coin toss on new patients?
Show: 50 patients × 20 visits, each patient's measurements their own plus small noise, diagnosis drawn at random
per patient; 30% held out. `train_test_split`: 0.93 to 0.98; `GroupShuffleSplit` by patient: 0.27 to 0.66
(chance, and wide: 15 test patients). 300 noise rows copied thrice: 0.92 to 0.99, deduplicated 0.41 to 0.61. A
random walk, day number as feature: shuffled split R² about 0.99; the last 20% of days held out, -0.15 to -4.3.
Explain: Rows in families (a person, a copy, the next day) must sit on one side, or the test measures memory.
Try: decide: the unit their future arrives in, and how to split by it; fix: their time-ordered data re-split by
date, the latest rows held out, the score before and after.
### 4
Need: My model's error is 16; is that good?
Show: two years of daily sales, a weekly pattern on a wandering level, noise sd 15, last 120 days held out. MAE:
training mean 32 to 71; same day last week 16 to 21; boosting on lags 13.5 to 25, behind last week in 4 of 15
seeds. Noise alone: 15·√(2/π) = 12.
Explain: A score means something between the baseline (knowing nothing) and the noise floor (knowing all).
Try: build: `DummyRegressor`, their current rule and their model on one split; predict: last week's
MAE from noise (√2 × 12 = 17), then check.
### 5
Need: How does `fit()` find the weights, and why does a bigger learning rate blow up?
Show: `y = 3x + 5` plus noise, x with sd 2, centred; one weight by gradient descent from 0. Rate 0.1: at the
exact 3.0 within about five steps. Rate 0.3: 6 to 8, then negative, swinging wider. A step
multiplies the error by 1 − 2·rate·mean(x²) (formula = run, 10 seeds): past rate 1/mean(x²), 0.21 to 0.29, it grows.
Explain: Each step moves the weight against the slope of the squared error, rate times slope; too big overshoots
further each time. (`LinearRegression` solves it in one calculation; `SGDRegressor` walks.)
Try: predict: a rooms coefficient alone, then beside floor area (price 3,000 a m² − 10,000 a room, rooms about
m²/25: about +53,000, then about -10,000); apply: their feature's divergence rate, 1/mean(x²), run.
### 6
Need: The model says 90%; can I tell the customer 90%?
Show: 20,000 rows; one signal (class means ±0.5, sd 1) in three near-identical columns, three noise columns.
Logistic and `GaussianNB` both 0.69 accurate; of rows called 0.85 to 0.95, logistic right 0.87 to 0.93, naive
Bayes 0.64 to 0.71. Naive Bayes counts the signal thrice, log-odds 3s: its "0.9" is sigmoid(ln 9 / 3) = 0.68.
Explain: `predict_proba` is a score until checked against outcomes; logistic regression adds log-odds, each unit
of a feature multiplying the odds by e^coef.
Try: apply: `calibration_curve` on their held-out rows, worst bin named; fix: that naive Bayes in
`CalibratedClassifierCV`, log loss 0.75-0.79 down to 0.59-0.60.
### 7
Need: "Fit the scaler on training rows only": does it change anything?
Show: predict both. `StandardScaler` on all rows before `cross_val_score` (five held-out scores averaged),
against inside a `Pipeline`: same to three decimals. `SelectKBest(k=20)` of 5,000 noise columns, 100 rows:
0.82 to 0.92 before; 0.42 to 0.62 inside (chance, on 100 rows).
Explain: A step that learns from rows learns the test fold if fitted before the split; a selector learns labels.
Try: fix: a notebook imputing and selecting on all rows, made one `Pipeline` until noise scores chance;
predict: `OneHotEncoder()` meeting a new value (`Found unknown categories`).
### 8
Need: My tree is 100% on training data; why does a shallow one beat it?
Show: `validation_curve` over `max_depth`, 2,000 rows, 10% labels flipped: the curves start together (depth 1)
and part, never cross; training climbs to 1.00; validation peaks at 0.77 to 0.87 at depth 3 to 8, then falls
0.02 to 0.06. Random labels: full tree 1.00 train, 0.48 to 0.52 test.
Explain: Splits that follow signal raise both scores (bias falls); splits that follow noise raise only training.
Try: apply: `validation_curve` for one knob of theirs, best value named; predict: a full tree on their data
with labels shuffled.
### 9
Need: My model is 98% accurate; why does everyone say it is useless?
Show: 30,000 rows, 2.5% fraud, thirds for training, validation, test; a miss costs 100, a review 5.
`DummyClassifier` 0.975, recall 0; logistic at 0.5, recall 0 to 0.28. The cheapest threshold on validation rows,
0.04 to 0.09 (formula 5/105 = 0.048): accuracy falls to 0.84-0.97, recall 0.35-0.59, test cost 16 to 38% lower.
Explain: Accuracy counts errors alike; act where costs cross, p = C_FP / (C_FP + C_FN), trusted only for
calibrated probabilities (step 6), so checked on validation.
Try: decide: their costs and the threshold validation picks; fix: oversampling before `cross_val_score`
(noise: recall 1.00) replaced by `class_weight` (AP 0.04 to 0.09, about the base rate).
### 10
Need: I kept the best of 200 settings by test score; why did it drop in production?
Show: noise labels, 200 test rows, 200 random trees: best test 0.525 to 0.59; on new rows 0.49 to 0.50.
Formula: one score wobbles √(0.25/200) = 0.035; the best of 200 independent scores sits 2.75 of those up, 0.60
(200 coin-flip guessers: 0.575 to 0.63). Trees from the same rows are related and reach less.
Explain: Choosing by a score chooses its luck too; tune by cross-validation, score the test set once.
Try: build: `GridSearchCV` around their whole pipeline with their split's folds, one test score; predict: how
far their best of 50 overstates.
### 11
Need: Which features does my forest really use?
Show: three real features, a random number, a random coin. Forest `feature_importances_`: random number 0.10 to
0.14, coin 0.01-0.02. `permutation_importance` on held-out rows: random number about 0, real ones 0.07 to 0.30.
Explain: Many distinct values offer many cuts that purify training rows by chance; held-out shuffling does not.
Try: apply: both importances for their model, a disagreement explained; decide: forest or boosting, by score
and fit time.
### 12
Need: The score is fine; how do I find what it gets wrong?
Show: 20,000 rows, 5% of labels mistyped; "north", 10% of rows, has an outcome that turns on a column the south
ignores; one logistic model. Error 0.16 to 0.19 overall; north 0.30 to 0.43, south 0.14 to 0.17. The 50 most
confident misses: 60 to 96% mistyped labels (all misses 23-29%). A north-only feature (north × that column):
north 0.08 to 0.15.
Explain: Errors cluster: by confidence they show bad labels, by segment whom the model fails; each names a fix.
Try: apply: their 30 most confident misses sorted into causes; build: error per affected group, the worst fixed.
### 13
Need: It was great in the notebook; why is it wrong in production when nothing crashed?
Show: a `joblib` pipeline: 0.77 to 0.99. Upstream sends `session_s` in milliseconds: about 0.50, one class for
every row, no warning (reordered columns do raise `The feature names should match`). Prices up 4% a month:
accuracy 0.75 to 0.68 in a year.
Explain: Nothing checks that serving inputs mean what training inputs meant; log them and compare. Input drift
is an alarm to check on fresh labels, not a verdict.
Try: build: a check of serving inputs' medians against training that fails on a unit change; predict: one input
shifting 3 sd, meaning kept (here accuracy ROSE, 0.75 to 0.82, where one class grew common; it fell, 0.80 to
about 0.60, where the outcome turned in a range the model never saw).

## Believable numbers
- [3,7,10] A leak: 0.85 to 1.00 on pure-noise labels.
- [4,10] Noise: chance ± √(p(1−p)/n): ±0.035 on 200 rows, ±0.016 on 1,000 (run: 0.48 to 0.52).
- [4] Baseline: the majority scores the class share; first models beat a good rule by 1 to 6 points here.
- [11] Fit, 100,000 × 20, 2 cores, here (November 2026): logistic about 0.1 s, boosting 1 to 3 s (30 s while
  other jobs held the cores), a forest of 100 trees 20 to 50 s.

## Go deep, leave for later
- Deep steps: 3, 9, 12 (splits and leakage, the measure and threshold the decision needs, and reading the errors: where scores that do not hold in use are made or caught).
- Later: neural networks (deep-learning-with-pytorch, planned), unsupervised learning, SVMs, fairness audits.

## Never omit
- Mathematics needed: algebra, reading graphs, mean and variance, logarithms (log loss, log-odds), probability as a share of cases; derivative only as slope.
- Look up when planned: library versions and names.

## Wrong beliefs
- [9] "99% accuracy means a good model" (at 99 to 1, always answering the majority scores 0.99 with zero recall).
- [8] "A model perfect on training data is excellent" (a full-depth tree fits random labels perfectly, then scores chance).
- [7] "Scaling all rows before splitting is harmless: the score barely moves" (for a scaler, often; the same habit with feature selection lifts pure noise far above chance).
- [9,10] "Oversample the rare class, then cross-validate" (copies land in both folds; on noise, recall looks perfect).
- [10] "Looking at test scores while tuning is fine" (the best of many models by test score looks good even on noise).
- [6,9] "`predict_proba` gives true probabilities" (only when calibrated; forests rarely reach near 0 or 1).
- [11] "`feature_importances_` shows what matters" (impurity importance favours many-valued features).

## Failures to diagnose
- [3] Great in cross-validation, poor on new people: one person's rows on both sides; `GroupKFold`.
- [2,12] A near-perfect score: a feature known only after the outcome, or computed from the label.
- [3,10] Far worse in use than in shuffled cross-validation on time-ordered data: the future leaked; `TimeSeriesSplit`.
- [7] `ValueError: Found unknown categories` at prediction: the encoder met a new category; `handle_unknown`.
- [12] One group's error far above the overall score: the model lacks a feature that matters only there; error per group shows it.
- [13] Quality decays after launch with no error: drift, or an upstream change of unit or meaning (every row one class).

## Practice and project
Guided: make each pitfall happen, read the number, change one thing. On your own: a public table from question to test score. Project: a model on the learner's own data or public data from their field; finish line: a report passing every "Judged by" test, a reloaded pipeline giving identical predictions, a monitoring plan.

## Mastery ladder
- Use: cross-validate a pipeline against a dummy baseline.
- Explain: find and name each leak in a given notebook, and predict how the score moves once fixed.
- Build: the project above.
- Design: for a stated decision, choose and defend the split, metric, threshold and retraining plan.

## Words to own
[1] supervised learning, feature, label; [2] class balance; [3] training set, validation set, test set,
data leakage; [4] baseline; [5] loss, gradient descent, coefficient; [6] log-odds, calibration; [7] pipeline, one-hot
encoding; [8] overfitting, bias, variance, regularisation; [9] confusion matrix, precision, recall, ROC curve,
threshold; [10] cross-validation, hyperparameter; [11] random forest, gradient boosting;
[12] error analysis; [13] training-serving skew, drift, monitoring
