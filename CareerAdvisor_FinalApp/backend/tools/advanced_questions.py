"""Advanced / expert question pool, written to ../app/data/skill_questions_advanced.json

Each skill gets 3 "advanced" (A) and 3 "expert" (X) questions. Together with the
2 easy + 2 intermediate questions from the original document they let the quiz
change with the student's experience level.

Run from the backend folder:   python tools/advanced_questions.py
Each row:  (tier, question, correct answer, wrong 1, wrong 2, wrong 3)
"""
import json
import re
import sys
from pathlib import Path

A, X = "advanced", "expert"

POOL = {
"Web Development": [
 (A, "A page loads slowly because large images block rendering. Which change most directly improves perceived load time?", "Serve appropriately sized, compressed images and lazy-load those below the fold", "Inline every image as base64 inside the HTML", "Disable browser caching so images are always fresh", "Convert all images to uncompressed bitmaps"),
 (A, "Which HTTP response header lets a site restrict which sources may run scripts, limiting the impact of XSS?", "Content-Security-Policy", "Accept-Language", "Content-Length", "ETag"),
 (A, "Which caching directive lets a browser show a cached copy immediately while fetching a fresh one in the background?", "stale-while-revalidate", "no-store", "must-revalidate with max-age=0", "Vary: *"),
 (X, "A content-heavy public site must rank well in search. Which factor should drive the choice between server-side rendering and a client-rendered SPA?", "Crawlability and time to first content for public pages versus interactivity needs", "Whichever framework is newest", "Avoiding any build step regardless of requirements", "The size of the developers' monitors"),
 (X, "Which set of metrics makes up Google's Core Web Vitals for real-user experience?", "Largest Contentful Paint, Interaction to Next Paint, Cumulative Layout Shift", "CPU temperature, RAM usage, disk speed", "Commit count, lines of code, build time", "Uptime, DNS TTL, TLS version"),
 (X, "Which practice most reduces the risk of a large front-end release?", "Feature flags with gradual rollout and fast rollback", "Releasing only on Fridays", "Skipping staging to ship faster", "Merging all changes in a single large commit"),
],
"Frontend Development": [
 (A, "In React, what stops an expensive child component from re-rendering when its props have not changed?", "Wrapping it with React.memo", "Calling forceUpdate in the parent", "Storing props in global variables", "Giving it a key that changes every render"),
 (A, "Why should items in a rendered list have stable, unique keys?", "So the framework can match items between renders and update only what changed", "So CSS can style each item differently", "So items sort alphabetically", "So the browser caches each item"),
 (A, "Which technique reduces the initial JavaScript bundle of a large single-page app?", "Code splitting with dynamic imports", "Minifying only the HTML", "Adding more polyfills", "Loading every route up front"),
 (X, "A design system is introduced across several product teams. What is its main benefit?", "Consistent, reusable components that reduce duplicated work and visual drift", "It removes the need for accessibility testing", "It guarantees faster servers", "It replaces version control"),
 (X, "What is the best way to make a complex interface accessible to screen-reader users?", "Use semantic HTML and add ARIA only where native semantics are insufficient", "Add ARIA roles to every div regardless of purpose", "Hide focus outlines for a cleaner look", "Convey state with colour alone"),
 (X, "Which principle is most sound when choosing a client state-management approach?", "Keep state as local as possible and lift it only when sharing requires it", "Put all state in one global store from the start", "Avoid state libraries in every project", "Duplicate server data in several stores for speed"),
],
"Backend Development": [
 (A, "Which technique prevents SQL injection when a backend builds queries from user input?", "Parameterized queries (prepared statements)", "Removing spaces from user input", "Using GET instead of POST", "Hiding the table names"),
 (A, "An endpoint must be safe to retry after a network timeout without creating duplicate orders. Which property is needed?", "Idempotency, for example through an idempotency key", "A longer response timeout", "A larger database instance", "A stateless frontend"),
 (A, "Which HTTP status code best tells a client it has sent too many requests?", "429 Too Many Requests", "401 Unauthorized", "404 Not Found", "502 Bad Gateway"),
 (X, "Which design choice most improves a backend's ability to scale horizontally?", "Keeping services stateless and storing session state in a shared store", "Storing sessions in each server's memory", "Running everything on one large server", "Writing logs only to local files"),
 (X, "A service keeps calling a failing downstream dependency and slows everything down. Which pattern helps?", "Circuit breaker with timeouts and fallbacks", "Retrying immediately in an infinite loop", "Growing the thread pool without limit", "Removing all timeouts"),
 (X, "Which practice best helps diagnose production issues across several services?", "Structured logging with correlation IDs plus metrics and tracing", "Printing debug output to the console only", "Disabling logs to save disk space", "Logging passwords to reproduce bugs"),
],
"Full-Stack Development": [
 (A, "A form submit should update the interface instantly even though the server may reject it. Which approach fits?", "An optimistic update with rollback if the server returns an error", "Blocking the UI until the page reloads", "Ignoring server validation", "Polling the database every millisecond"),
 (A, "Where should input validation be enforced in a full-stack app?", "On the server always, and on the client for usability", "Only on the client", "Only in database table names", "Nowhere if the UI hides invalid options"),
 (A, "Which approach keeps frontend and backend aligned on request and response shapes?", "A shared, versioned API contract such as OpenAPI with generated types", "Informal chat messages between developers", "Copying JSON examples into comments", "Letting each side guess field names"),
 (X, "A team splits work between frontend and backend developers. What most reduces integration problems?", "Agreeing on the API contract first and mocking it for parallel work", "Building the frontend only after the backend is complete", "Avoiding any documentation", "Using different data formats on each page"),
 (X, "Which deployment practice best supports reliable full-stack releases?", "A CI/CD pipeline that runs automated tests before deployment", "Manual uploads to the production server", "Deploying untested hotfixes directly", "Disabling tests that fail occasionally"),
 (X, "Which practice reduces the risk of token theft through XSS in a browser app?", "Short-lived access tokens with refresh tokens in HttpOnly, Secure cookies", "Long-lived tokens in localStorage", "Tokens in URL query strings", "Passwords stored in cookies"),
],
"Mobile App Development": [
 (A, "Why should network calls not run on a mobile app's main (UI) thread?", "They can freeze the interface and cause dropped frames or not-responding errors", "They only drain battery when idle", "The operating system forbids networking", "They always corrupt local storage"),
 (A, "Which strategy keeps a mobile app useful with poor connectivity?", "Local caching with background sync and conflict handling", "Showing a blank screen until online", "Forcing users to restart the app", "Requesting network access repeatedly in a loop"),
 (A, "Why request runtime permissions only when a feature needs them?", "It builds user trust and respects privacy while meeting platform rules", "It makes the app compile faster", "It removes the need for a privacy policy", "It increases battery capacity"),
 (X, "A small team must support Android and iOS. Which factors matter most when choosing cross-platform or native development?", "Performance needs, device features, team skills and long-term maintenance", "Which language has the shortest name", "Whether the icon fits the logo", "The number of store screenshots"),
 (X, "Which release practice limits risk when shipping a mobile update?", "Staged rollout with crash monitoring and a rollback plan", "Releasing to all users at once without monitoring", "Skipping beta testing", "Removing crash reporting to improve ratings"),
 (X, "How should sensitive secrets such as API keys be handled in a mobile app?", "Keep them on a backend and use short-lived tokens in the app", "Hard-code them in the app for convenience", "Store them in plain-text preferences", "Print them in release logs"),
],
"Data Analytics": [
 (A, "A dataset has many missing values in a key column. What is the best first step?", "Investigate why values are missing before choosing to drop, impute or flag them", "Delete the whole dataset", "Fill every gap with zero", "Ignore the column silently"),
 (A, "Which chart best shows the distribution of one numeric variable?", "Histogram", "Pie chart", "Line chart of categories", "Stacked area chart"),
 (A, "Two variables are strongly correlated. What can you conclude?", "They move together, but correlation alone does not prove causation", "One definitely causes the other", "There is no relationship", "The data must be wrong"),
 (X, "An A/B test shows a small uplift. Which check matters most before acting on it?", "Whether sample size and statistical significance support the result", "Whether the chart colours look good", "Whether the test ran on a Friday", "Whether the uplift matches a manager's expectation"),
 (X, "Which practice most improves trust in a company-wide KPI dashboard?", "Documented metric definitions with a single governed source of truth", "Letting each team compute the metric its own way", "Hiding the calculation logic", "Updating numbers manually without records"),
 (X, "What is the risk described by Simpson's paradox?", "A trend visible in subgroups can reverse when the groups are combined", "Averages always increase with more data", "Data becomes encrypted", "Charts stop rendering"),
],
"Artificial Intelligence": [
 (A, "What does an admissible heuristic guarantee for the A* search algorithm?", "It never overestimates the true cost to the goal, so A* finds an optimal path", "It always runs in constant time", "It ignores path cost", "It overestimates cost to move faster"),
 (A, "What is the main idea of reinforcement learning?", "An agent learns actions by receiving rewards or penalties from an environment", "A model is trained only on labelled images", "Data is clustered without any feedback", "Rules are written manually by experts only"),
 (A, "What is a key limitation of rule-based expert systems?", "They are hard to maintain and do not learn from new data automatically", "They cannot produce any output", "They require GPUs", "They always overfit"),
 (X, "Before deploying an AI system that affects people, which step is most important?", "Assess bias, safety and accountability, and keep human oversight for high-impact decisions", "Deploy first and review complaints later", "Remove all documentation", "Rely on training-set accuracy alone"),
 (X, "How should you decide whether an AI feature is worth building?", "Define the problem and success metrics, then compare against a simple baseline", "Use the most complex model available", "Skip measurement because AI is inherently better", "Measure only the model's size"),
 (X, "What does model drift mean in production?", "Performance degrades because real-world data changes over time", "The model file moves to another server", "The model trains faster each day", "The code editor changes theme"),
],
"Machine Learning": [
 (A, "A model has 99% training accuracy but 70% test accuracy. What is the most likely cause?", "Overfitting", "Underfitting", "Perfect generalization", "Too little training data labelled"),
 (A, "On a dataset where only 1% of cases are positive, why is accuracy a poor metric?", "A model that always predicts negative scores 99% while finding no positives", "Accuracy cannot be computed for imbalanced data", "Accuracy only applies to regression", "Accuracy ignores the test set"),
 (A, "What is the purpose of cross-validation?", "Estimating how well a model generalizes by training and testing on different splits", "Increasing the number of features", "Making training faster by skipping data", "Encrypting the training data"),
 (X, "What is data leakage?", "Information from outside the training data, such as test or future data, influences the model", "Losing files from the server", "Encrypting the dataset twice", "Training with too few epochs"),
 (X, "Which regularization technique can shrink some coefficients exactly to zero?", "L1 (Lasso) regularization", "L2 (Ridge) regularization", "Dropout in random forests", "Min-max scaling"),
 (X, "For a high-stakes decision, why might a simpler interpretable model be preferred?", "Stakeholders can understand, audit and challenge its decisions", "Simple models always have higher accuracy", "Interpretable models need no validation", "They never need monitoring"),
],
"Generative AI": [
 (A, "What does hallucination mean for a language model?", "Producing fluent but incorrect or unsupported content", "Refusing to answer", "Running out of memory", "Translating text"),
 (A, "Which problem does retrieval-augmented generation (RAG) mainly address?", "Grounding answers in external, up-to-date documents to reduce unsupported claims", "Making the model smaller", "Removing the need for prompts", "Training from scratch for every query"),
 (A, "Which prompt change most reliably improves structured output?", "Specifying the exact output schema and requesting only that format", "Writing the prompt in capital letters", "Using the shortest prompt possible", "Asking the model to guess the format"),
 (X, "What is prompt injection?", "Untrusted input that tries to override or manipulate the model's instructions", "Adding tokens to a prompt for speed", "A GPU optimization", "A way of compressing the model"),
 (X, "A company wants to use an LLM with customer data. Which governance step matters most?", "Data-handling rules covering privacy, retention, provider terms and human review", "Pasting data into any public tool", "Disabling logging of all access", "Assuming the vendor handles all compliance automatically"),
 (X, "Which approach best evaluates an LLM feature before launch?", "A representative test set with defined criteria, plus human review of failures", "Trying three prompts and trusting the best one", "Relying on the model's own claim of accuracy", "Measuring only response length"),
],
"Cybersecurity": [
 (A, "Which attack tricks users into revealing credentials by impersonating a trusted party?", "Phishing", "SQL injection", "Denial of service", "Port scanning"),
 (A, "What does the principle of least privilege mean?", "Users and services get only the access they need for their tasks", "Everyone shares one admin account", "Access is permanent once granted", "Only managers need passwords"),
 (A, "Why is multi-factor authentication effective?", "A stolen password alone is not enough to sign in", "It removes the need for passwords entirely", "It encrypts all network traffic", "It blocks malware downloads"),
 (X, "After a confirmed breach, what should come first in incident response?", "Contain the incident and preserve evidence before eradication and recovery", "Delete all logs immediately", "Announce blame publicly", "Restore systems without investigating"),
 (X, "What is the purpose of a security risk assessment?", "Prioritizing controls by the likelihood and impact of threats to assets", "Buying the most expensive tools", "Eliminating all risk entirely", "Documenting only past incidents"),
 (X, "Which security model assumes no implicit trust and verifies every request?", "Zero Trust", "Perimeter-only security", "Security through obscurity", "Open trust networking"),
],
"Cloud Computing": [
 (A, "Which service model provides a managed runtime and deployment without managing servers?", "Platform as a Service (PaaS)", "Infrastructure as a Service (IaaS)", "On-premises hosting", "Colocation"),
 (A, "What is the main benefit of auto-scaling?", "Capacity follows demand, balancing cost and performance", "Servers never fail", "Costs are always fixed", "Code deploys itself without tests"),
 (A, "Why distribute an application across multiple availability zones?", "To keep it running if one data-centre zone fails", "To reduce the number of users", "To make DNS unnecessary", "To avoid backups"),
 (X, "Which practice best controls unexpected cloud spending?", "Tagging resources, setting budgets and alerts, and reviewing usage regularly", "Leaving unused instances running", "Using the largest instance sizes by default", "Disabling billing alerts"),
 (X, "What does the shared responsibility model say?", "The provider secures the cloud infrastructure; the customer secures what they put in it", "The provider handles all security", "The customer secures the provider's data centres", "Security is optional for small workloads"),
 (X, "What is infrastructure as code mainly used for?", "Defining infrastructure in version-controlled, repeatable templates", "Writing documentation only", "Configuring servers manually but faster", "Replacing monitoring"),
],
"Database Management": [
 (A, "What is the main trade-off of adding an index to a table?", "Faster lookups at the cost of extra storage and slower writes", "It encrypts the table data", "It makes every row unique automatically", "It removes the need for primary keys"),
 (A, "Which transaction property ensures a transaction either fully completes or has no effect?", "Atomicity", "Isolation", "Durability", "Normalization"),
 (A, "A query on a large table is slow. What should you check first?", "The query plan, to see whether it uses a suitable index", "Whether the table name is long", "Adding more columns", "Dropping the primary key"),
 (X, "When is denormalization reasonable?", "When read performance needs justify controlled redundancy", "Always, to save design time", "Never under any circumstance", "Only when there are no queries"),
 (X, "Which backup strategy best supports disaster recovery?", "Regular backups stored off-site and tested with restore drills", "A single backup on the same server", "Backups that are never tested", "Relying on the primary database only"),
 (X, "What does the CAP theorem say about a distributed database during a network partition?", "You must trade off consistency against availability", "You can have all three guarantees at once", "Partitions never occur", "Only availability matters"),
],
"Data Engineering": [
 (A, "What is the difference between ETL and ELT?", "ETL transforms data before loading; ELT loads raw data first and transforms it in the warehouse", "ETL is only for images", "ELT never uses SQL", "They are identical"),
 (A, "Why make data-pipeline steps idempotent?", "So re-running a step after failure does not duplicate or corrupt data", "To make the pipeline slower", "To avoid scheduling", "To remove logging"),
 (A, "Why partition a large table by date?", "To improve query performance and manageability by scanning only relevant partitions", "To encrypt each row", "To remove duplicate users", "To avoid indexes forever"),
 (X, "Which practice best protects downstream users from broken data?", "Automated data-quality checks and schema validation with alerting", "Checking data manually once a year", "Ignoring schema changes", "Deleting failed records silently"),
 (X, "When is stream processing preferred over batch?", "When results are needed within seconds or minutes of events occurring", "When data arrives once a month", "When latency does not matter", "When storage is unavailable"),
 (X, "What is the main value of data lineage?", "Tracing where data came from and how it was transformed, for trust and debugging", "Making files smaller", "Randomizing records", "Replacing access documentation"),
],
"Blockchain": [
 (A, "What makes a blockchain ledger tamper-resistant?", "Each block includes the previous block's hash, and changes require network consensus", "Data is stored on one central server", "Blocks are deleted after use", "Only one person can read the ledger"),
 (A, "What does a smart contract do?", "Executes coded rules automatically on a blockchain when conditions are met", "Prints legal documents", "Stores passwords offline", "Mines new coins"),
 (A, "How does Proof of Work differ from Proof of Stake?", "Proof of Work uses computing effort and much energy; Proof of Stake selects validators by staked value", "Proof of Work needs no computers", "Proof of Stake uses no consensus", "They are the same algorithm"),
 (X, "Which question is most important when deciding whether a project needs a blockchain at all?", "Whether multiple parties who do not trust each other need a shared, tamper-evident record", "Whether the project has a logo", "Whether a token can be created", "Whether a database is unavailable"),
 (X, "What is a common smart-contract risk?", "Exploitable bugs such as reentrancy, made worse because deployed code is hard to change", "Contracts running too slowly on paper", "Contracts being unable to hold value", "Contracts needing no testing"),
 (X, "What is the main purpose of a Merkle tree in a blockchain?", "Efficiently verifying that data is included in a block using hashes", "Compressing images", "Storing private keys", "Choosing the next miner randomly"),
],
"Internet of Things (IoT)": [
 (A, "Which protocol is lightweight and widely used to publish sensor data over unreliable networks?", "MQTT", "FTP", "SMTP", "RDP"),
 (A, "Why is over-the-air (OTA) firmware update capability important?", "It lets manufacturers patch security flaws and bugs in deployed devices", "It removes the need for sensors", "It makes devices lighter", "It disables authentication"),
 (A, "What is edge computing in IoT?", "Processing data near the device to reduce latency and bandwidth use", "Processing only in a distant archive", "Removing the network", "Encrypting sensors physically"),
 (X, "Which practice most improves the security of a large IoT deployment?", "Unique device credentials, encrypted communication and signed firmware updates", "Shared default passwords on all devices", "Open ports for easy access", "Plain-text data transmission"),
 (X, "A battery-powered sensor must last for years. Which design choice helps most?", "Duty cycling with deep sleep, sending data only when needed", "Polling continuously at maximum rate", "Using the highest transmit power always", "Keeping the radio always on"),
 (X, "What must an IoT platform plan for when device counts grow into thousands?", "Device identity, provisioning, monitoring and lifecycle management at scale", "Manual configuration of each device", "Ignoring failed devices", "A single shared credential"),
],
"UI/UX Design": [
 (A, "What is the main goal of usability testing?", "Observing real users to find where the design causes problems", "Checking that colours match the logo", "Getting managers' approval", "Counting the number of screens"),
 (A, "Which guideline helps users with colour-vision deficiency?", "Do not rely on colour alone; add labels, icons or patterns", "Use only red and green", "Remove all text", "Use very low contrast"),
 (A, "What does a design system provide?", "Reusable components and guidelines for consistent design", "Automatic user research", "Server hosting", "Marketing copy"),
 (X, "A stakeholder requests a feature that tests show confuses users. What is the best response?", "Present the user evidence, explore alternatives and test again", "Ship it without changes", "Ignore the stakeholder", "Hide the confusing step"),
 (X, "Which measures directly capture task efficiency in usability studies?", "Time on task and task success rate", "Number of colours used", "Font file size", "Count of design meetings"),
 (X, "What is the purpose of a user journey map?", "Visualizing the steps, needs and pain points users experience over time", "Listing server endpoints", "Estimating hosting costs", "Naming brand colours"),
],
"Computer Networking": [
 (A, "Which OSI layer is responsible for routing packets between networks?", "Network layer", "Data link layer", "Transport layer", "Session layer"),
 (A, "How does TCP differ from UDP?", "TCP gives reliable, ordered delivery; UDP is connectionless with lower overhead", "UDP guarantees delivery and TCP does not", "TCP works only on wireless links", "They are identical"),
 (A, "What is the purpose of subnetting?", "Dividing a network into smaller segments for efficiency, security and address management", "Increasing the speed of light", "Encrypting packets", "Removing routers"),
 (X, "A network is congested at peak hours. What is the most appropriate first diagnostic step?", "Monitor traffic and identify sources and bottlenecks before changing hardware", "Replace all cables immediately", "Disable monitoring", "Add random firewall rules"),
 (X, "Which design improves network resilience?", "Redundant links and devices with failover", "A single switch for everything", "No spare capacity", "Shared admin passwords"),
 (X, "What is the role of a firewall in network security?", "Filtering traffic according to defined security policies", "Assigning IP addresses", "Caching web pages only", "Increasing bandwidth"),
],
"AR/VR Development": [
 (A, "Which factor matters most for reducing motion sickness in VR?", "A stable, high frame rate with low motion-to-photon latency", "A very low frame rate for a cinematic feel", "Frequent sudden camera shakes", "Variable latency spikes"),
 (A, "What does six degrees of freedom (6DoF) tracking capture?", "Position (x, y, z) and rotation (pitch, yaw, roll)", "Six separate headsets", "Six colour channels", "Six network layers"),
 (A, "Which technique helps AR content stay anchored to the real world?", "SLAM or plane/feature tracking that maps the environment", "Placing content randomly every frame", "Disabling the camera", "Using only GPS indoors"),
 (X, "Which design practice makes VR experiences comfortable?", "Comfort options such as teleport movement, vignettes and adjustable settings", "Forcing constant fast artificial movement", "Removing all user controls", "Ignoring different user heights"),
 (X, "What is an effective way to optimize a heavy VR scene?", "Reduce draw calls and polygon counts, use levels of detail and baked lighting", "Add more real-time lights", "Use the highest-resolution textures everywhere", "Disable culling"),
 (X, "What is critical when rolling out AR/VR training in an organization?", "Hardware management, safety, content updates and measurable learning outcomes", "Graphics quality only", "Skipping user testing", "Avoiding any feedback"),
],
"Technical Support": [
 (A, "A user says they cannot log in. What should you do first?", "Gather details and reproduce the problem, then check account status and recent changes", "Reinstall the operating system", "Tell them to buy a new device", "Close the ticket"),
 (A, "What is the benefit of a knowledge base for a support team?", "Faster, consistent resolutions and fewer repeated escalations", "Removing the need for training", "Longer call times", "Fewer customers"),
 (A, "How should multiple tickets be prioritized?", "By impact and urgency, following service-level agreements", "Alphabetical order", "Newest ticket first always", "The loudest customer first"),
 (X, "Which practice reduces recurring incidents?", "Root-cause analysis and permanent fixes tracked as problems", "Repeating the same temporary workaround", "Closing tickets quickly without notes", "Blaming users"),
 (X, "What is an SLA?", "An agreement defining expected service levels such as response and resolution times", "A type of server", "A programming language", "A password policy"),
 (X, "How should you explain a technical issue to a non-technical user?", "Use plain language, confirm understanding and give clear next steps", "Use as much jargon as possible", "Skip the details", "Ask them to read the documentation"),
],
"IT Infrastructure": [
 (A, "What is the main purpose of virtualization?", "Running several isolated systems on shared hardware to improve utilization", "Removing the need for networks", "Encrypting storage", "Replacing backups"),
 (A, "Which RAID level mirrors data across disks for redundancy?", "RAID 1", "RAID 0", "JBOD (just a bunch of disks)", "No RAID level offers redundancy"),
 (A, "Why apply patches on a regular schedule?", "To close known vulnerabilities and fix defects under managed testing", "To slow systems down", "To delete user data", "To avoid change control"),
 (X, "Which pair of metrics describes disaster-recovery targets?", "RTO (recovery time objective) and RPO (recovery point objective)", "CPU and RAM", "SLA and NDA", "DNS and DHCP"),
 (X, "What does capacity planning aim to do?", "Ensure resources meet forecast demand without costly over-provisioning", "Buy as much hardware as possible", "Ignore growth", "Eliminate monitoring"),
 (X, "Which practice makes infrastructure changes safer?", "Change management with testing, approvals and rollback plans", "Making changes in production at random", "Skipping documentation", "Having no maintenance windows"),
],
"Research & Development": [
 (A, "What is the purpose of a literature review in an R&D project?", "Understanding existing work to identify gaps and avoid duplication", "Increasing the budget", "Replacing experiments", "Writing the final report first"),
 (A, "Why use a control group in an experiment?", "To compare outcomes and isolate the effect of the change being tested", "To increase sample size only", "To make results look better", "To avoid statistics"),
 (A, "What does reproducibility mean in research?", "Others can obtain the same results using the same methods and data", "Results never change under any method", "Only the author can repeat it", "The study is published twice"),
 (X, "How should an R&D team decide which ideas to fund?", "Compare potential value, feasibility, risk and alignment with strategy", "Fund the loudest advocate", "Fund every idea equally", "Fund only the cheapest idea"),
 (X, "What is a stage-gate process?", "Structured review points where projects are evaluated before continuing", "A type of laboratory door", "A software licence", "A marketing campaign"),
 (X, "Why protect intellectual property early in R&D?", "To secure rights to inventions before public disclosure", "To avoid documentation", "To delay research", "To prevent peer review entirely"),
],
"Communication": [
 (A, "What is active listening?", "Fully attending, confirming understanding and responding to what the speaker says", "Waiting for your turn to speak", "Interrupting to correct", "Checking your phone while nodding"),
 (A, "How should bad news be delivered to a team?", "Be clear and honest, explain the reasons and outline next steps", "Hide the details", "Blame individuals", "Send it late at night without context"),
 (A, "Which channel suits a sensitive, complex discussion best?", "A live conversation such as a call or meeting", "A group chat emoji", "A one-line text", "An all-staff email"),
 (X, "How should a message be adapted for senior executives?", "Lead with the conclusion, impact and decision needed, with detail on request", "Start with a long background history", "Use technical jargon only", "Avoid stating a recommendation"),
 (X, "What is the best way to handle conflict in a meeting?", "Acknowledge views, focus on the issue and seek shared goals", "Ignore it", "Take sides publicly", "End the meeting abruptly"),
 (X, "What makes feedback constructive?", "It is specific, timely, behaviour-focused and offers a way to improve", "It is vague and personal", "It is given months later", "It is only praise"),
],
"Leadership": [
 (A, "Which action best shows servant leadership?", "Removing obstacles so the team can do its best work", "Taking credit for results", "Controlling every task", "Avoiding team input"),
 (A, "How should a leader handle a mistake of their own?", "Own it, explain what happened and fix the process", "Blame a junior colleague", "Hide it", "Wait for someone to notice"),
 (A, "Why set clear expectations?", "People know what success looks like and can be held accountable fairly", "To reduce all questions", "To avoid feedback", "To increase workload"),
 (X, "A high performer is hurting team morale with poor behaviour. What should a leader do?", "Address the behaviour directly with clear expectations and consequences", "Ignore it because results are good", "Dismiss the whole team", "Promote them immediately"),
 (X, "How should a leader drive change in an organization?", "Communicate the vision, involve people and support them through the transition", "Announce it without explanation", "Change everything silently at once", "Avoid addressing resistance"),
 (X, "What is the best way to develop future leaders?", "Delegate meaningful responsibility with coaching and feedback", "Keep all decisions centralized", "Give no feedback", "Hire only external leaders"),
],
"Team Management": [
 (A, "What is the most effective way to run a team meeting?", "Share an agenda, keep to time and record decisions and actions", "Hold it without a purpose", "Let one person talk the whole time", "Skip follow-up"),
 (A, "How should work be assigned fairly?", "Match tasks to skills and workload while sharing development opportunities", "Always give the hardest work to the same person", "Assign randomly without information", "Give tasks only to friends"),
 (A, "What is a good approach when a team misses a deadline?", "Review the causes together and adjust the plan or resources", "Blame the slowest member publicly", "Extend deadlines forever", "Ignore the issue"),
 (X, "Which practice best supports a remote or hybrid team?", "Clear communication norms, regular check-ins and shared documentation", "Constant surveillance only", "No expectations for response time", "Meetings with no agenda"),
 (X, "How can a manager handle an underperforming employee?", "Give specific feedback, set goals, provide support and follow up", "Wait for the annual review only", "Complain to colleagues", "Reassign tasks silently"),
 (X, "What does psychological safety enable in a team?", "Members can raise concerns and mistakes without fear of blame", "Fewer ideas", "Less accountability", "No conflict ever"),
],
"Project Management": [
 (A, "What is the critical path in a project schedule?", "The longest sequence of dependent tasks, which sets the minimum project duration", "The most expensive tasks", "The tasks done by the manager", "The first tasks listed"),
 (A, "What is scope creep?", "Uncontrolled growth of project scope without adjusting time or budget", "A reduction in team size", "A budget surplus", "A planned release"),
 (A, "Which tool helps identify project risks early?", "A risk register reviewed regularly", "A seating chart", "A colour palette", "A holiday calendar"),
 (X, "A project is behind schedule. What is a sound response?", "Analyze the cause, re-plan, and negotiate scope, resources or schedule with stakeholders", "Hide the delay until the deadline", "Add people without analysis", "Drop quality checks silently"),
 (X, "What is earned value management used for?", "Comparing planned and actual progress and cost to forecast performance", "Selecting team names", "Designing logos", "Scheduling holidays"),
 (X, "When is an agile approach most suitable?", "When requirements are uncertain and frequent feedback is valuable", "When nothing may change", "When no customer is involved", "When there is no team"),
],
"Marketing": [
 (A, "What is market segmentation?", "Dividing a market into groups with similar needs in order to target them effectively", "Raising prices for everyone", "Copying competitors", "Stopping advertising"),
 (A, "What does the positioning of a product describe?", "How it is perceived relative to competitors in customers' minds", "Where the warehouse is", "The product's weight", "The number of staff"),
 (A, "Which metric shows the cost of gaining one new customer?", "Customer acquisition cost (CAC)", "Click-through rate", "Page views", "Share of voice"),
 (X, "A campaign has high clicks but low sales. What should be investigated?", "The landing page, audience fit and conversion path", "Only the logo", "Nothing, because clicks are enough", "Stop measuring"),
 (X, "How should a marketing budget be allocated across channels?", "Based on measured return, audience reach and strategic goals", "Equally across all channels regardless of results", "Only to the newest channel", "Randomly"),
 (X, "What is the value of customer lifetime value (CLV)?", "It estimates total revenue from a customer, guiding how much to invest in acquiring them", "It measures website speed", "It counts social followers", "It is the product's price"),
],
"Digital Marketing": [
 (A, "What does SEO aim to improve?", "Visibility in organic search results", "Paid ad bids only", "Email delivery speed", "Server uptime"),
 (A, "Which metric shows the share of visitors who complete a desired action?", "Conversion rate", "Bounce rate", "Impressions", "Frequency"),
 (A, "Why use UTM parameters on campaign links?", "To track which campaigns and channels drive traffic", "To speed up the page", "To encrypt the URL", "To block bots"),
 (X, "What is the best way to A/B test an email subject line?", "Test one variable on comparable audience segments and measure the results", "Change everything at once", "Test on a single recipient", "Pick the winner by opinion"),
 (X, "How does remarketing work?", "Showing ads to people who previously visited your site or engaged with your brand", "Showing ads to random strangers only", "Deleting cookies", "Sending the same email twice"),
 (X, "Which practice supports privacy-compliant marketing?", "Collecting consent, explaining data use and honouring opt-outs", "Buying random email lists", "Hiding unsubscribe links", "Tracking without notice"),
],
"Sales": [
 (A, "What is the purpose of qualifying a lead?", "Determining whether the prospect has the need, budget, authority and timing to buy", "Sending more emails", "Lowering the price", "Skipping discovery"),
 (A, "Which approach handles price objections best?", "Understand the concern and reinforce value before discussing price changes", "Immediately discounting", "Arguing with the customer", "Ignoring the objection"),
 (A, "What is a sales pipeline?", "A staged view of prospects as they move toward closing", "A list of products", "A delivery schedule", "A marketing calendar"),
 (X, "How should a salesperson build long-term accounts?", "Understand the client's goals and provide ongoing value beyond the first sale", "Disappear after closing", "Focus only on quotas", "Avoid follow-up"),
 (X, "Which measure best forecasts future revenue?", "Weighted pipeline value based on stage conversion rates", "Number of calls made only", "Total company headcount", "Office size"),
 (X, "What is consultative selling?", "Asking questions and tailoring a solution to the customer's problem", "Reading a script without listening", "Selling the cheapest item", "Pressuring the customer to close"),
],
"Business Development": [
 (A, "What is the main goal of business development?", "Creating long-term value through new markets, partnerships and growth opportunities", "Processing payroll", "Fixing office equipment", "Writing code"),
 (A, "What does a SWOT analysis examine?", "Strengths, weaknesses, opportunities and threats", "Sales, wages, orders and taxes", "Suppliers, workers, outlets and timing", "Standards, wiring, overheads and tools"),
 (A, "What is due diligence before a partnership?", "Investigating the partner's finances, legal standing and reputation before committing", "Signing quickly to save time", "Skipping legal review", "Relying on rumours"),
 (X, "Which factors matter most when evaluating entry into a new market?", "Market size, competition, regulation and fit with capabilities", "Whether competitors dislike it", "Only the CEO's preference", "The number of office plants"),
 (X, "How should partnership terms be structured?", "With clear objectives, roles, metrics and exit conditions", "Verbal agreements only", "Open-ended and without goals", "Hidden from stakeholders"),
 (X, "What is a go-to-market strategy?", "A plan for reaching target customers and gaining competitive advantage with a product", "A schedule for office cleaning", "A software architecture", "A hiring policy"),
],
"Customer Service": [
 (A, "How should you first respond to an upset customer?", "Listen, empathize and acknowledge the problem before offering solutions", "Defend the company immediately", "Transfer them repeatedly", "End the conversation"),
 (A, "What does first-contact resolution measure?", "The share of issues solved in the customer's first interaction", "Calls answered by the manager", "The number of agents", "Hold music quality"),
 (A, "Which behaviour builds trust with customers?", "Setting realistic expectations and following through", "Promising what cannot be delivered", "Avoiding updates", "Blaming other departments"),
 (X, "A customer's request violates policy. What is a good approach?", "Explain the reason politely and offer the best available alternative", "Break the policy secretly", "Refuse without explanation", "Argue about the policy"),
 (X, "How can customer feedback improve a service?", "Analyzing themes and acting on them, with follow-up", "Ignoring negative comments", "Collecting it but never reading it", "Deleting complaints"),
 (X, "Which metric measures customer loyalty and likelihood to recommend?", "Net Promoter Score (NPS)", "Average handle time", "Server uptime", "Ticket count"),
],
"Content Writing": [
 (A, "What should come first before writing content?", "Defining the audience and purpose", "Choosing the font", "Writing only the headline", "Copying a competitor"),
 (A, "Why use headings and short paragraphs in web content?", "They improve scanability and readability", "They hide the content", "They reduce search visibility", "They slow readers down"),
 (A, "What is a call to action (CTA)?", "A prompt telling readers what step to take next", "A legal disclaimer", "A footnote", "A spelling check"),
 (X, "How should content be adapted for different channels?", "Keep the core message but adjust format, tone and length for each channel", "Post identical text everywhere", "Use only long formats", "Ignore audience behaviour"),
 (X, "What is plagiarism and how is it avoided?", "Using others' work without credit; avoid it by citing sources and writing original text", "Quoting with permission", "Editing your own draft", "Using headings"),
 (X, "Which measure best shows content effectiveness?", "Engagement and conversions against the content's goal", "Word count only", "Number of drafts", "Font size"),
],
"Social Media Management": [
 (A, "What is a content calendar used for?", "Planning and scheduling posts for consistency", "Counting followers", "Blocking trolls", "Designing logos"),
 (A, "Which metric measures how people interact with posts?", "Engagement rate", "Server latency", "Domain age", "Email open rate"),
 (A, "How should negative comments be handled?", "Respond professionally, move issues offline when needed and avoid deleting legitimate criticism", "Delete all criticism", "Argue publicly", "Ignore every comment"),
 (X, "How should social platforms be chosen?", "Match platforms to where the target audience is active and to campaign goals", "Use every platform equally", "Pick the newest platform", "Pick at random"),
 (X, "How should a brand prepare for a social media crisis?", "Have a response plan with roles, approved messaging and monitoring", "Wait to see if it goes away", "Delete the accounts", "Respond emotionally"),
 (X, "What is social listening?", "Monitoring mentions and conversations to understand sentiment and trends", "Reading only your own posts", "Muting competitors", "Buying followers"),
],
"Event Management": [
 (A, "What should be defined first when planning an event?", "Objectives, audience, budget and date", "The catering menu only", "The seating colours", "The photographer"),
 (A, "Why prepare a contingency plan?", "To handle problems such as weather or vendor failure with minimal disruption", "To reduce attendees", "To avoid budgeting", "To skip risk review"),
 (A, "What is a run-of-show?", "A detailed timeline of event activities and responsibilities", "A ticket price list", "A venue brochure", "A guest survey"),
 (X, "How should an event's success be measured?", "Against predefined goals such as attendance, satisfaction and return on investment", "By how loud it was", "By staff opinion only", "It should not be measured"),
 (X, "What matters when negotiating with event vendors?", "Clear contracts covering scope, costs, timelines and cancellation terms", "Verbal promises only", "Choosing the cheapest without checks", "Having no written agreement"),
 (X, "How can safety be ensured at large events?", "Risk assessment, crowd management, emergency plans and regulatory compliance", "Relying on luck", "Ignoring capacity limits", "Skipping the staff briefing"),
],
"Teaching & Training": [
 (A, "What makes a learning objective effective?", "It is specific and measurable", "It is vague and broad", "It describes only the teacher's activity", "It has no assessment"),
 (A, "What is formative assessment?", "Ongoing checks during learning to guide improvement", "A final exam only", "A graduation ceremony", "A certificate"),
 (A, "Why use varied activities in a session?", "To maintain engagement and support different learning preferences", "To confuse learners", "To avoid planning", "To shorten the session"),
 (X, "How should training effectiveness be evaluated?", "Measure learning, behaviour change and results, for example with the Kirkpatrick levels", "By attendance only", "By trainer popularity", "It should not be evaluated"),
 (X, "How can a trainer handle mixed-ability learners?", "Differentiate tasks and provide support and extension activities", "Teach to the fastest only", "Ignore struggling learners", "Use one pace for everyone"),
 (X, "What is the purpose of scaffolding in teaching?", "Providing temporary support that is gradually removed as learners gain skill", "Constructing buildings", "Removing all help at once", "Adding unrelated tasks"),
],
"Administration": [
 (A, "What is the benefit of a good filing system?", "Quick retrieval and secure organization of records", "More paper", "Hiding documents", "A slower workflow"),
 (A, "How should confidential documents be handled?", "Restrict access, store securely and dispose of them properly", "Leave them on a desk", "Share them with everyone", "Email them without protection"),
 (A, "What is the purpose of meeting minutes?", "Recording decisions and actions", "Counting attendees only", "Timing breaks", "Listing snacks"),
 (X, "How should an administrator prioritize competing requests?", "By urgency, impact and deadlines, communicating clearly", "First come only", "Loudest first", "Avoiding all of them"),
 (X, "What does process improvement in administration involve?", "Mapping workflows, removing waste and measuring results", "Adding approval steps everywhere", "Ignoring complaints", "Keeping inefficiency"),
 (X, "Which is a good practice for budget tracking?", "Recording expenses against approved budgets with regular review", "Estimating at year-end only", "Keeping no receipts", "Sharing no reports"),
],
"Hospitality Management": [
 (A, "What does RevPAR measure in a hotel?", "Revenue per available room", "Reservations per area", "Rating per advertised room", "Revenue per arriving resident"),
 (A, "How should service failures be handled?", "Apologize, fix the issue quickly and follow up", "Deny the problem", "Blame the guest", "Offer nothing"),
 (A, "Why is staff training important in hospitality?", "It gives consistent service quality and safety", "It raises noise levels", "It lowers guest satisfaction", "It reduces hygiene"),
 (X, "How can a hotel manage seasonal demand?", "Dynamic pricing, forecasting and flexible staffing", "Fixed prices all year", "Closing without planning", "Ignoring data"),
 (X, "What is the role of HACCP in food service?", "Identifying and controlling food-safety hazards", "Menu pricing", "Staff scheduling", "Interior design"),
 (X, "Which measure reflects guest satisfaction?", "Guest review scores and Net Promoter Score", "Number of towels", "Lobby size", "Parking spaces"),
],
"Advertising": [
 (A, "What is a target audience?", "The specific group an advertisement aims to reach", "Everyone in the world", "The advertising team", "Competitors only"),
 (A, "What does reach measure in advertising?", "The number of unique people exposed to an ad", "Clicks only", "Ad budget", "Ad size"),
 (A, "What is a unique selling proposition (USP)?", "A distinct benefit that differentiates a product from competitors", "A discount code", "A legal notice", "A brand font"),
 (X, "How should an advertising campaign's ROI be assessed?", "Compare incremental revenue or goal outcomes against campaign cost", "By number of awards", "By creative opinion only", "By budget size"),
 (X, "What is the main purpose of media planning?", "Selecting channels and timing to reach the audience efficiently", "Choosing office furniture", "Writing legal terms", "Hiring staff"),
 (X, "Why is ethical advertising important?", "Avoiding misleading claims maintains trust and meets regulations", "Exaggeration boosts credibility", "Rules do not apply to ads", "Trust is irrelevant"),
],
"Brand Management": [
 (A, "What is brand identity?", "The visual and verbal elements a company uses to present its brand", "The company's tax number", "A product's weight", "Employee count"),
 (A, "What does brand equity represent?", "The value a brand adds beyond the product itself", "Office rent", "Inventory count", "Delivery cost"),
 (A, "Why keep brand messaging consistent?", "Consistency builds recognition and trust", "It confuses customers", "It lowers quality", "It only increases cost"),
 (X, "How should a brand extend into a new category?", "Check fit with brand values and customer perception before launching", "Extend into anything", "Ignore research", "Copy competitors blindly"),
 (X, "What is a brand audit?", "A review of the brand's position, perception and performance", "A financial tax filing", "A product recall", "A staff attendance check"),
 (X, "How should a brand respond to a reputation crisis?", "Acknowledge issues transparently, act on fixes and communicate consistently", "Stay silent forever", "Deny without evidence", "Delete all channels"),
],
"Market Research": [
 (A, "What is primary research?", "Collecting new data directly from sources such as surveys and interviews", "Reading existing reports only", "Guessing", "Copying competitors' data"),
 (A, "Why does sample representativeness matter?", "Conclusions can be generalized to the target population", "It makes surveys longer", "It lowers cost", "It avoids analysis"),
 (A, "Which survey question best avoids bias?", "A neutral, clearly worded question", "A leading question", "A double-barrelled question", "A loaded question"),
 (X, "What is the difference between qualitative and quantitative research?", "Qualitative explores motivations in depth; quantitative measures numerically across larger samples", "They use the same methods", "Quantitative research has no numbers", "Qualitative research needs no participants"),
 (X, "How should research findings be reported to decision-makers?", "With clear insights, evidence and recommended actions", "As raw data without context", "Only the unflattering results", "As jargon-heavy tables only"),
 (X, "What is market sizing used for?", "Estimating the demand and revenue potential of a market", "Measuring store area", "Counting employees", "Choosing a logo"),
],
"Strategy & Planning": [
 (A, "What is a strategic objective?", "A measurable goal that supports the organization's long-term direction", "A daily to-do item", "A vague wish", "A job title"),
 (A, "What does a balanced scorecard do?", "Tracks performance across financial, customer, process and learning perspectives", "Tracks only profit", "Replaces strategy", "Lists employees"),
 (A, "Why monitor progress against plans?", "To detect deviations early and adjust", "To avoid decisions", "To increase paperwork", "To justify no change"),
 (X, "What is the purpose of scenario planning?", "Preparing for several possible futures and uncertainties", "Predicting one exact future", "Avoiding risk analysis", "Planning only for the best case"),
 (X, "How should resources be allocated across strategic initiatives?", "By expected impact, risk and alignment with priorities", "Equally regardless of value", "To the loudest team", "By seniority only"),
 (X, "What is the role of KPIs in strategy execution?", "Providing measurable indicators of progress toward strategic goals", "Decorating reports", "Replacing goals", "Measuring unrelated activity"),
],
}

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def main():
    here = Path(__file__).resolve().parent.parent / "app" / "data"
    base = json.loads((here / "skill_questions.json").read_text(encoding="utf-8"))
    problems = []
    if set(POOL) != set(base):
        problems.append(f"skill names differ: {sorted(set(POOL) ^ set(base))}")
    out = {}
    for skill, rows in POOL.items():
        counts = {A: 0, X: 0}
        items = []
        for tier, q, ok, *bad in rows:
            counts[tier] += 1
            opts = [ok] + bad
            if len(bad) != 3 or len(set(opts)) != 4:
                problems.append(f"{skill}: bad options in '{q[:40]}'")
            items.append({"id": f"{slug(skill)}-{'a' if tier == A else 'x'}{counts[tier]}",
                          "level": tier, "topic": "Applied" if tier == A else "Expert / strategic",
                          "question": q, "options": opts, "answer": ok})
        if counts != {A: 3, X: 3}:
            problems.append(f"{skill}: need 3 advanced + 3 expert, got {counts}")
        out[skill] = items
    if problems:
        sys.exit("Problems:\n - " + "\n - ".join(problems))
    (here / "skill_questions_advanced.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(out)} skills, {sum(len(v) for v in out.values())} advanced/expert questions")

if __name__ == "__main__":
    main()
