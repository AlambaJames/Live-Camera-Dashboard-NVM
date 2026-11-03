# Campus VMS (Video Management System)
A secure, self-hosted, and lightweight Video Management System designed specifically for university campus network infrastructure. Built with Flask, SQLite, and MediaMTX to provide full on-premise control over local NVR hardware and camera feeds.

##  Key Features
* ** Role-Based Admin Authentication:** Secure staff profiles featuring unique staff IDs, office positions (e.g., *Senior Network Engineer*), and hashed credentials.
* ** Privileged Action Protection:** Requires active admin password/PIN verification before permitting critical security actions like adding or removing administrators.
* ** Comprehensive Audit Trail:** Automated activity logging that records system and configuration events stamped with the responsible admin's name and title.
* ** UI-Driven Settings Panel:** Easily configure NVR hardware connection parameters (IP, RTSP port, credentials) and auto-deletion retention policies directly from the dashboard.
* ** Local Network First:** Operates entirely on-premise over local LAN/switch configurations with zero external cloud dependencies.

##  Tech Stack
* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug Security
* **Database:** SQLite
* **Streaming Proxy:** MediaMTX
* **Frontend:** Jinja2 Templates, Custom Dark UI (CSS)
