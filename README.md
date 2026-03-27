## RadFlow: Real-Time Radiology Workflow Assistant

RadFlow is a real-time radiology workflow assistant designed to improve the speed, accuracy, and safety of ultrasound in high-volume, resource-constrained hospital environments. It streamlines the entire ultrasound workflow, from patient registration to scan review and report generation, with a focus on usability and automation.

---

## Live Demo
Access the project at: [https://mosfet.onrender.com/]

---

## Login Credentials
**Admin**  
Email: `admin23@gmail.com`  
Password: `SecurdeP@sseeword123`

---

## How RadFlow Works
1. **Login:** Use the admin credentials above to access the system.
2. **Add a Patient:** Go to the dashboard, enter patient details, and select or input the clinical context.
3. **Start Scan:** Begin the ultrasound session.
4. **View Scans:** Access simulated ultrasound videos (breast, fetal, abdominal).
5. **Alerts:** Receive alerts when a scan is completed or an abnormality is detected.
6. **Review Abnormalities:** Radiologists can review alerts, confirm findings, and capture relevant images.
7. **Finalize Reports:** Review and complete the scan reports.
8. **Backend Integration:** All data is stored and retrieved via the Node.js/MongoDB backend.

> **Note:** Features like automated reporting currently use dummy data for demonstration purposes.

---

##  Technical Details
- **Monorepo:** Frontend (Next.js/React + Tailwind CSS) and backend (FastAPI, Python, MongoDB) integrated in a single repository.
- **Notifications & Simulations:** Dummy data is used for notifications and ultrasound video simulations.
- **Backend:** FastAPI (Python) with MongoDB for data storage.
- **Frontend:** Next.js (React) for a modern, responsive UI.
- **Authentication:** JWT-based authentication for secure access.
- **Environment Variables:** See `backend/.env.example` for required variables.

---

## Backend Repository
[Backend Source Code](https://github.com/Summiedev/mosfet/tree/main/backend)

---


## Team Members & Contributions

### 1. Apatira Sumayyah — Core Architect & Backend Developer
- Led the overall system architecture and design.
- Implemented complex business logic and handled integration between frontend and backend modules.
- Ensured seamless workflow and robust error handling across the application.

### 2. Shotunde Maryam — Backend/API Developer
- Designed and developed RESTful APIs for all major features.
- Managed database operations, schema design, and data integrity.
- Implemented authentication and authorization mechanisms.

### 3. Bolarinwa Abdullah — Frontend Developer
- Built and styled the user interface components.
- Integrated frontend with backend APIs for real-time data flow.
- Focused on responsive design and user experience improvements.

### 4. Apatira Sofiyyah — UI/UX Designer
- Led user research and requirements gathering.
- Designed the entire user experience and interface using Figma.
- Ensured accessibility and usability best practices throughout the design.

---
