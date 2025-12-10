# BEDI: A Comprehensive Benchmark for Evaluating Embodied Agents on UAVs
This project introduces **BEDI (Benchmark for Embodied Drone Intelligence)**, a comprehensive and standardized evaluation framework for UAV-Embodied Agents (UAV-EAs) in autonomous tasks. BEDI leverages the dynamic capabilities of Vision-Language Models (VLMs) and incorporates a novel Dynamic Chain-of-Embodied-Task paradigm, which decomposes complex UAV tasks into standardized, measurable subtasks based on the perception-decision-action loop. The benchmark evaluates UAV-EAs across five core sub-skills: semantic perception, spatial perception, motion control, tool utilization, and task planning. Additionally, BEDI integrates static real-world environments with dynamic virtual scenarios, offering a hybrid testing platform that allows for flexible task customization and scenario extension. By providing open, standardized interfaces and conducting empirical evaluations, BEDI identifies limitations in current UAV-EA models and paves the way for future advancements in embodied intelligence research and model optimization.

<p align="center" width="100%">
  <img src="imgs/image1.png" width="100%" alt="BEDI Overview">
</p>

## The Composition of the Testing Environment for BEDI
We have collected real UAV imagery to construct a representative real-world test dataset for static testing, while also creating a dynamic virtual testing environment using Unreal Engine (UE) and AirSim to support interaction with UAV-EAs. To facilitate evaluation, BEDI includes task-specific evaluation metrics and interaction interfaces. The platform consists of three core components:

* Test environments (static real-world and dynamic virtual)
* Open interaction interfaces
* Evaluation metrics (for both static and dynamic tasks)



## Release Notes
* **[2025/12/10]  🚀 Update: Action-Capability Test Samples & Real-World Dynamic UAV Scenarios**
  We have uploaded additional **action-capability benchmark samples**, together with **dynamic test scenarios constructed from real UAV video frames**.
  * 🧾 **Action-Capability Evaluation (Standardized Drone Action Template)**
    To benchmark action execution, we provide a **standard UAV action template**. The agent is required to **translate natural-language instructions into the template-formatted commands**, enabling the drone system to **directly parse and execute** them. This setting evaluates the agent’s instruction understanding, structured command generation, and action feasibility under a unified interface.
  * 🎬 **Dynamic Scenario Tasks (Real UAV Frames)**
    * **Fine-Grained Vehicle Recognition Task**: From a distant aerial viewpoint, the agent must plan the most efficient and shortest flight path to capture critical visual details and identify the fine-grained vehicle model (e.g., Mercedes-Benz or Audi). The system supports corrective feedback (e.g., re-perception/backtracking or ground-level reference photos after misidentification). Performance is quantified by **average perception/decision scores across nodes** and **total execution steps**.
    * **Dynamic Rider Tracking Task**: The agent must maintain persistent tracking of a continuously moving rider under illumination changes, occlusions, and distractions, adapting its strategy based on evolving visual cues. Performance is measured by **average perception/decision scores across nodes**, reflecting stability, adaptability, and decision consistency.
      
    The newly added test dataset is also available at the following link ([https://huggingface.co/datasets/GuoMN/BEDI](https://huggingface.co/datasets/GuoMN/BEDI)), under the `BEDI-1.5` directory. In addition, the corresponding evaluation code has been uploaded to the `test` folder.

- **[2025/07/22]  🚀 Release of Dynamic Virtual Environment & Benchmark Test Platform**We have developed a Dynamic Virtual Environment based on **[Unreal Engine 4.27](https://dev.epicgames.com/documentation/zh-cn/unreal-engine/unreal-engine-4-27-documentation?application_version=4.27)**, integrated with a programmable drone system through **[AirSim](https://github.com/microsoft/AirSim)**. Building upon AirSim's drone control API, we performed further encapsulation and refactoring, designed and implemented a set of core control interfaces, and constructed a Drone Control Server based on these interfaces.Furthermore, we built the web-based frontend interface of the test platform using **[PixelStreaming](https://docs.unrealengine.com/4.27/en-US/SharingAndReleasing/PixelStreaming/)** technology, allowing users to *quickly evaluate and test the performance of embodied agents* directly through a web browser.
  * 🌐 Dynamic Virtual Environment
    * Built on **Unreal Engine 4.27**
    * Includes three representative scenarios: Cargo Port, Burning Building, Urban City Blocks
    * Enables users to design various **embodied tasks** based on these environments
  * 🛫 Drone Control Server
    * Provides core interfaces for drone control, including perception (e.g., Retrieve camera images), action (e.g., fly forward, land), and state (e.g., Get drone pose) APIs
    * Supports real-time interaction with drones in the virtual environment
  * 🖥️ Pixel Streaming Frontend Interface
    * Built using **Pixel Streaming** technology for real-time browser interaction
    * Custom UI layout based on the default Pixel Streaming interface
    * Supports interaction with AirSim Drone Control Server and Embodied Agents
    * Key features include task switching, real-time visualization of task execution, and free-form dialogue with embodied agents
  
- **[2025/07/01] 🔥 Release of the Static Image Test Dataset 1.0** The dataset covers two types of perception questions (Semantic Perception, Spatial Perception) and three types of decision-making questions (Motion Control, Tool Utilization, Task Planning). The specific sample composition included in the dataset is as follows:

  * 154 images for perception evaluation, 2,740 total perception-related questions
    * 1,020 semantic discrimination questions
    * 422 semantic description questions
    * 582 semantic target determination questions
    * 455 spatial direction questions
    * 261 spatial distance questions
  * 30 images for decision-making evaluation, 357 total decision-related questions
    * 140 motion control questions
    * 114 tool utilization questions
    * 103 task planning questions
  
  The dataset can be obtained from the following link: (https://huggingface.co/datasets/GuoMN/BEDI). At the same time, the evaluation code for the static image experiment results has also been uploaded in the `test` folder.



## 🚀 Deployment and Usage Guide

### 📦 1. Install Node.js (Optional)

If you haven't already installed **Node.js**, you can download and install it from the [official website](https://nodejs.org/en/download/).
### 📂 2. Clone the Repository

Begin by cloning the **BEDI** repository to your local machine:

```bash
git clone https://github.com/lostwolves/BEDI.git
```

### 🧪 3. Download the Dynamic Virtual Environment

You can download the **Dynamic Virtual Environment** from [Hugging Face](https://huggingface.co/datasets/GuoMN/BEDI-UE):

```bash
huggingface-cli download --repo-type dataset --resume-download GuoMN/BEDI-UE --local-dir ./UE
```
<p align="center" width="100%">
  <img src="env.png" width="100%" alt="Dynamic Virtual Environment">
</p>

### ⚙️ 4. Configure and Start the Dynamic Virtual Environment

* ⚙️ Configure the Pixel Streaming Settings

  Navigate to the following directory:

  ```
  WindowsNoEditor/Samples/PixelStreaming/WebServers/SignallingWebServer/platform_scripts/cmd
  ```

  Run the following script:

  ```bash
  run_local.bat
  ```

  This will automatically install **Chocolatey**, **npm**, and **Node.js**, and start the **Signalling Server**.

  Alternatively, you can run the shortcut file:

  ```
  run_local.bat - 快捷方式
  ```

  located in the `WindowsNoEditor` directory.

* 🎮 Configure the Unreal Engine Project

  Go to the `WindowsNoEditor` directory and modify the shortcut file:

  ```
  ship.exe - 快捷方式
  ```

  - Set **Start in**: Path to the `WindowsNoEditor` directory.
  - Set **Target**: Path to the `ship.exe` file.

* ▶️ Launch the Unreal Engine Project

  Run the shortcut file `ship.exe - 快捷方式` to start the Unreal Engine application.

* 🌐 Access the Pixel Streaming Interface

  Open your web browser and navigate to:

  ```
  http://127.0.0.1
  ```

  If the **Pixel Streaming UI** appears, click the **"Click to Start"** button to begin streaming.

### 🧰 5. Install Required Dependencies

Navigate to the `AirSim_Server` directory and create a new Conda environment:

```bash
cd AirSim_Server
conda create -n airsim python=3.12 -y
conda activate airsim
```

Install the required dependencies:

```bash
pip install numpy==2.0.0 msgpack-rpc-python==0.4.1 backports.ssl_match_hostname
pip install -r requirements.txt
```

📌 **Tip**: If you encounter issues, refer to this [Zhihu article](https://zhuanlan.zhihu.com/p/63093901) for detailed configuration and troubleshooting.

### 🖥️ 6. Start the Backend Server (Task Server & AirSim Control Server)

From the `AirSim_Server` directory, start the backend server:

```bash
python main.py
```

### 🧠 7. Start Your Task

Once everything is running, open your web browser and access the interface.

- 📋 **Select a Task**: Choose a task from the dropdown menu and click **"Start Task"**.
- 💬 **Interact with the Agent**: Input your question in the text box and click **"Send"** to interact.

---

🎉 Congratulations! You're all set to use the **BEDI** system. Enjoy exploring and executing tasks in your dynamic virtual environment!
