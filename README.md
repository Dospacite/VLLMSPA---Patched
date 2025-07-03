# Vulnerable LLM Single Page Web App

## Installation
### Linux with NVIDIA
Make sure you install NVIDIA Container Toolkit from https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
Then execute the following: 
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

### Other Installations - Not Recommended
Not running the container with a GPU makes the LLM response times painfully slow.
Make sure you remove the lines 45-47 in the docker-compose.yaml file to not use the NVIDIA runtime.
### Steps after running the docker container
Execute `docker ps` to see the running containers and note down the ollama container name, usually vllmspa-ollama-1.
Then execute `docker exec vllmspa-ollama-1 ollama pull llama3.1:8b-instruct-q8_0` to install the model.

## Vulnerability Coverage of OWASP 2023 LLM

### LLM01: Prompt Injection
Available through the message fetch tool, where the messages are passed back from the tool without sanitization. The tool accepts unsanitized user input that can be used for injection attacks.

### LLM02: Insecure Output Handling
This will be available through the unsanitized handling of LLM response via the message summarizer, using dangerouslySetHTML.

### LLM03: Training Data Poisoning
Will be implemented through insecure RAG entries, as a form of "Send Feedback to The LLM" feature.

### LLM04: Model Denial of Service
No safeguards exist against mass requests to the /chat endpoint.

### LLM05: Supply Chain - TODO
Will use an intentionally vulnerable version of a python package.

### LLM06: Sensitive Information Disclosure
Exposes private messages to the attacker through the message fetching tool. The tool returns all messages including private ones without proper authorization checks.

### LLM07: Insecure Plugin Design
Command injection vulnerability in model info tool, will also implement user information access through raw sql query, to enable SQL injection.

### LLM08: Excessive Agency - TODO
Planned to be implemented by enabling LLM to read the "privacy statement" on the website, but will have the ability to modify the statement as well.

### LLM09: Overreliance
This is low-priority right now. Maybe I can implement this by enabling a "post summary message" tool, where the LLM gathers recent messages and posts a message claiming that they were from real authorative sources.

### LLM10: Model Theft
This is already implemented since there is no safeguard against usage of this model without logging in, or no rate limits.

## Vulnerability Coverage of OWASP 2025 LLM
Only the vulnerabilities not covered by the 2023.

### LLM07: System Prompt Leakage
Did not separate system and human prompt.

### LLM08: Vector and Embedding Weakness - TODO

### LLM09: Misinformation - TODO

### LLM10: Unbounded Consumption - TODO
Maybe a fake wallet that decreases in funds every time a "request" is performed by the LLM.


