# ♻️ EcoSort

### AI-Powered Smart Waste Segregation Bin

> **One Bin. Zero Sorting Decisions.**

EcoSort is an AI-powered smart waste segregation system designed to automatically identify and sort waste into **Biodegradable, Non-Biodegradable, and Recyclable** categories.

The core idea is simple: instead of asking people to decide which bin an item belongs in, **EcoSort makes the classification decision automatically** using a camera, AI-based classification, and a mechanical sorting mechanism.

---

## 🚨 Problem

Waste segregation often depends on people correctly identifying and disposing of waste into the appropriate bin.

This creates several problems:

* ❌ People may not reliably identify the correct waste category.
* ❌ Incorrect sorting contaminates otherwise usable waste streams.
* ❌ Awareness posters do not guarantee correct behavior.
* ❌ Manual segregation requires additional human effort.
* ❌ The same problem exists across **colleges, hostels, hotels, restaurants, offices, and other institutions**.

### The Core Problem

**Waste segregation shouldn't depend entirely on human decisions.**

EcoSort moves the responsibility from the user to the system.

---

## 💡 Our Solution

EcoSort combines:

📷 **Camera**
↓
🧠 **AI Classification**
↓
⚙️ **Automatic Mechanical Sorting**
↓
🗑️ **Correct Waste Compartment**

The system is designed around a single smart bin containing multiple compartments.

When a user disposes of an item:

1. The camera captures the waste item.
2. The AI system analyzes the captured image.
3. The item is classified into a waste category.
4. The mechanical mechanism directs the item into the corresponding compartment.

### Waste Categories

| Category            | Description                                    |
| ------------------- | ---------------------------------------------- |
| 🟢 Biodegradable    | Organic / biodegradable waste                  |
| ⚫ Non-Biodegradable | Waste that does not naturally decompose easily |
| 🔵 Recyclable       | Materials that can be recovered and recycled   |

---

## 🏗️ Product Architecture

```text
                  ┌──────────────────┐
                  │   Waste Item     │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │     Camera       │
                  │   ESP32-CAM      │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  AI Classifier   │
                  │                  │
                  │ Biodegradable    │
                  │ Non-Biodegradable│
                  │ Recyclable       │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Sorting Control  │
                  │   / Controller   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Mechanical Flap  │
                  │     / Chute      │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Bio      │ │ Non-Bio  │ │Recycle   │
        │ Waste    │ │ Waste    │ │ Waste    │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 🧪 Current Proof of Concept

The current project includes a **web/app classification demo**.

The demo allows a user to capture/provide an image and receive a waste category prediction.

### Important

The web/app demo is **not the final physical product**.

It exists to demonstrate and validate the **AI classification component**, which is intended to become the "brain" of the physical EcoSort bin.

The physical smart bin is the actual product vision.

---

## 🔧 Hardware Components

The planned physical prototype uses affordable and readily available components.

| Component                        |     Estimated Cost |
| -------------------------------- | -----------------: |
| ESP32-CAM                        |               ₹700 |
| 1–2 Servo Motors                 |          ₹200–₹300 |
| IR / Ultrasonic Sensor           |          ₹100–₹200 |
| Motor/Servo Driver + Electronics |          ₹100–₹200 |
| Power Supply                     |          ₹200–₹300 |
| Mechanical Flap / Chute          |          ₹300–₹500 |
| DIY 3-Compartment Bin Body       |          ₹500–₹800 |
| Wires, Screws, Brackets etc.     |          ₹200–₹300 |
| **Estimated Prototype Cost**     | **~₹2,300–₹3,300** |

> These are prototype estimates, not final production costs.

The component estimates and prototype approach are based on the current EcoSort concept presentation.

---

## 💰 Why EcoSort Can Be Affordable

EcoSort is designed around relatively low-cost components rather than expensive dedicated computing hardware.

At larger production volumes, costs can potentially be reduced through:

* Bulk component procurement
* Standardized mechanical design
* Manufacturing optimization
* Better component selection

---

## 🆚 Existing Approach vs EcoSort

| Existing Approach       | Problem                             | EcoSort                      |
| ----------------------- | ----------------------------------- | ---------------------------- |
| Multiple labeled bins   | User must identify the correct bin  | One smart bin                |
| Awareness posters       | Awareness doesn't guarantee action  | Automated decision           |
| Manual segregation      | Requires human effort               | Automatic sorting            |
| Fixed labels/categories | Ambiguous items can cause confusion | AI-based classification      |
| Sorting after disposal  | Errors already enter waste stream   | Decision happens at disposal |

EcoSort does not claim that existing waste-management systems are useless. Instead, it addresses one specific weakness:

> **Current systems often place the responsibility of correct segregation on the user. EcoSort attempts to move that responsibility to the system.**

---

## 🎯 Target Market

EcoSort is initially focused on institutional and commercial environments where waste segregation happens repeatedly.

### Initial Targets

* 🎓 Colleges & Universities
* 🏫 Hostels
* 🏨 Hotels
* 🍽️ Restaurants
* 🏢 Offices
* 🏙️ Commercial Facilities

The initial strategy is to target institutional deployments first and then expand into hospitality and commercial environments.

---

## 💼 Business Model

EcoSort follows a **B2B / institutional model**.

### 1. Smart Bin Sales

Sell EcoSort units to:

* Colleges
* Universities
* Hotels
* Restaurants
* Offices
* Commercial facilities

### 2. AI / Monitoring / Maintenance Subscription

Potential recurring services include:

* Software updates
* Device monitoring
* Analytics
* Maintenance
* Classification-model improvements

### 3. AMC / Maintenance Contracts

Annual maintenance and servicing for deployed EcoSort units.

```text
Hardware Sale
      +
Annual Software / Service
      +
Maintenance Contract
      =
Recurring Business Model
```

The current presentation describes the unit economics as illustrative assumptions rather than actual pricing.

---

## 📊 Market Opportunity

EcoSort is positioned within the growing smart waste-management market.

The current project presentation identifies:

* **Global Smart Waste Management Market:** US$3.54B estimated for 2025
* **Projected Global Market:** US$7.15B by 2030
* **Indian Smart Waste Management Market:** US$90.04M estimated for 2025

The initial Serviceable Obtainable Market is defined as an internal bottom-up estimate focused on campuses and commercial customers in selected Indian cities, rather than a published market figure.

---

## 🛣️ Roadmap

EcoSort is currently at the **concept + AI proof-of-concept stage**.

```text
┌─────────────────────┐
│ AI Classification   │
│ Demo + Concept      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Physical Prototype  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Campus Deployment   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Hotels • Restaurants│
│ • Offices           │
└─────────────────────┘
```

### Future Goals

* Build the physical prototype
* Integrate the AI classifier with the hardware
* Implement automatic mechanical sorting
* Test the system in a campus environment
* Improve classification accuracy
* Collect real-world waste data
* Expand into hotels, restaurants, and offices

The current roadmap explicitly follows **AI demo → physical prototype → campus deployment → commercial expansion**.

---

## 🔮 Future Improvements

Potential future additions include:

* 📈 Waste analytics dashboard
* 📡 Remote device monitoring
* 🔔 Full-bin notifications
* 📊 Waste-category statistics
* 🤖 Improved AI classification models
* 🔄 Continuous model improvement from real-world data
* 🌐 Multi-device monitoring for institutions
* 🔧 Remote diagnostics and maintenance tracking

These are future possibilities, not features currently claimed as implemented.

---

## ⚠️ Current Status

| Component                    | Status             |
| ---------------------------- | ------------------ |
| AI Classification Concept    | ✅ Demonstrated     |
| Web/App Classification Demo  | ✅ Proof of Concept |
| Physical Smart Bin           | 🚧 Planned         |
| Automatic Mechanical Sorting | 🚧 Planned         |
| Campus Deployment            | 🔜 Future          |
| Commercial Deployment        | 🔜 Future          |
| Large-scale Production       | 🔜 Future          |

**Current focus:** turning the AI proof of concept into a functional physical prototype.

---

## 👥 Team

| Member                     | Responsibility            |
| -------------------------- | ------------------------- |
| **Vaibhav Singh Kushwaha** | AI / Classification Model |
| **Shiva Chaurasiya**       | AI Integration / API      |
| **Shivam Chaudhary**       | Backend & Systems         |
| **Riya Kushwaha**          | Presentation & Strategy   |

Team roles are based on the EcoSort project presentation.

---

## 🌱 Vision

EcoSort aims to make waste segregation **automatic at the point of disposal**.

Instead of expecting every person to understand every waste category, the system should make the classification decision automatically.

> **EcoSort turns waste segregation from a human responsibility into an automated system.**

### ♻️ One Bin. Zero Sorting Decisions.

---

## 📌 Project Status

**EcoSort — Ideathon 2026**

**Problem Statement #4 — Waste Segregation Awareness**

Built as a concept and proof-of-concept project with the vision of developing an affordable, AI-powered physical waste segregation system.

---

## 📄 Disclaimer

The market figures, prototype costs, selling-price examples, and unit economics presented in this repository are **estimates/assumptions for the current ideathon concept** and should not be interpreted as finalized commercial pricing or independently validated market projections.

The physical EcoSort bin is currently a **roadmap item**, while the web/app component serves as a proof of concept for AI classification.
