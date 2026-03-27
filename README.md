## RadFlow: Real-Time Radiology Workflow Assistant

RadFlow is a real-time radiology workflow assistant designed to improve the speed, accuracy, and safety of ultrasound in high-volume, resource-constrained hospital environments. It improves the entire ultrasound workflow: ensuring every scan has a clear clinical indication, reducing missed diagnoses, {especially in: Breast ultrasound (cancer detection), Fetal ultrasound (maternal and fetal anomalies) and Abdominal Ultrasound}; eliminating incomplete scans through structured guidance; reduce reporting time via automation and enables early detection and prioritization of critical cases.


---

## Live Demo
Access the project at: [https://mosfet.onrender.com/]

---

## Login Credentials
**Admin**  
  Email   : `demo@radflow.com`
  Password: `radflow123`
  Role    : `hybrid (full access)`
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
## UI/UX screens
---<img width="1553" height="949" alt="Login" src="https://github.com/user-attachments/assets/6e09fa6b-8b41-41f9-a3fd-1d0235f2f4f7" />
<img width="1553" height="944" alt="Login(1)" src="https://github.com/user-attachments/assets/910136c2-4e4a-4015-b509-0e4535735737" />
<img width="1553" height="944" alt="OTP" src="https://github.com/user-attachments/assets/8a7a2626-9480-4bc1-8074-53c4f280b034" />
<img width="1553" height="944" alt="dashboard" src="https://github.com/user-attachments/assets/bab9a1e5-72dc-482f-9490-4f40e7fe793d" />
<img width="1553" height="1073" alt="new scan" src="https://github.com/user-attachments/assets/e9be2d0b-35a2-4701-97ec-6900714a01ca" />
<img width="1553" height="1052" alt="sscan view" src="https://github.com/user-attachments/assets/ed83e837-35b4-48aa-afc5-4d9f0f2799c2" />
<img width="1553" height="1052" alt="sscan view(1)" src="https://github.com/user-attachments/assets/1ab1cefc-9f3c-44a4-8655-0898752e4f04" />
<img width="1553" height="944" alt="Create Styleguide Page" src="https://github.com/user-attachments/assets/f619e347-8e4f-4b3c-ae69-11446bbd9e0a" />
<img width="1553" height="1052" alt="Create Styleguide Page(1)" src="https://github.com/user-attachments/assets/c1e4a538-43d3-477f-b5a5-7c2d82d72a29" />
<img width="1553" height="1102" alt="review" src="https://github.com/user-attachments/assets/00e471f4-ecea-4182-a8e7-70fbd2c8aa94" />
<img width="1553" height="944" alt="report successful(1)" src="https://github.com/user-attachments/assets/dcfc6d6c-a0bf-406b-80e3-750b1f5757c1" />
<img width="1553" height="944" alt="report successful" src="https://github.com/user-attachments/assets/11f584af-f5b6-487a-abf8-e207e6b637c1" />
---

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





