import sys
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QTimeEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate, QTime, QDateTime

class Citas(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        layout = QVBoxLayout()

        self.setWindowTitle("Clinica-UGB")
        self.setGeometry(100, 100, 300, 300)

        self.label_paciente = QLabel("Nombre del Paciente:")
        self.input_paciente = QLineEdit(self)
        layout.addWidget(self.label_paciente)
        layout.addWidget(self.input_paciente)

        self.label_doctor = QLabel("Nombre del Doctor:")
        self.input_doctor = QLineEdit(self)
        layout.addWidget(self.label_doctor)
        layout.addWidget(self.input_doctor)

        self.label_fecha = QLabel("Fecha de la Cita:")
        self.dateEdit = QDateEdit(self)
        self.dateEdit.setMinimumDate(QDate.currentDate())  # Definimos fecha actual
        layout.addWidget(self.label_fecha)
        layout.addWidget(self.dateEdit)

        self.label_hora = QLabel("Hora de la Cita:")
        self.timeEdit = QTimeEdit(self)
        layout.addWidget(self.label_hora)
        layout.addWidget(self.timeEdit)

        self.label_email = QLabel("Correo:")
        self.input_email = QLineEdit(self)
        layout.addWidget(self.label_email)
        layout.addWidget(self.input_email)

        self.button = QPushButton("Registrar Cita", self)
        self.button.clicked.connect(self.registerAppointment)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def initDB(self):
        # Creamos una base de datos para almacenar las citas registradas
        self.conn = sqlite3.connect("citas.db")
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente TEXT NOT NULL,
                doctor TEXT NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                correo TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def registerAppointment(self):
        paciente_nombre = self.input_paciente.text()
        nombre_doctor = self.input_doctor.text()
        cita_fecha = self.dateEdit.date().toString("yyyy-MM-dd")
        cita_hora = self.timeEdit.time().toString("HH:mm")
        enviar_correo = self.input_email.text()

        # Aqui identificamos si ya existe una cita en la misma fecha y hora
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM citas WHERE fecha = ? AND hora = ?
        """, (cita_fecha, cita_hora))
        existing_appointment = cursor.fetchone()

        if existing_appointment:
            QMessageBox.warning(self, "Cupo lleno", "Ya existe una cita programada para esta fecha y hora.")
            return

        # Determinamos que la fecha y hora de la cita sean futuras
        current_date_time = QDateTime.currentDateTime()
        appointment_date_time = QDateTime(self.dateEdit.date(), self.timeEdit.time())

        if appointment_date_time < current_date_time:
            QMessageBox.warning(self, "Fecha inválida", "La fecha y hora de la cita deben ser en el futuro.")
            return

        # Insertamos los registros a la base de datos
        cursor.execute("""
            INSERT INTO citas (paciente, doctor, fecha, hora, correo) 
            VALUES (?, ?, ?, ?, ?)
        """, (paciente_nombre, nombre_doctor, cita_fecha, cita_hora, enviar_correo))
        self.conn.commit()

        self.sendConfirmationEmail(paciente_nombre, nombre_doctor, cita_fecha, cita_hora, enviar_correo)

    def sendConfirmationEmail(self, paciente_nombre, nombre_doctor, cita_fecha, cita_hora, enviar_correo):
        sender_email = "clinicaugb@gmail.com"  
        sender_password = "yqoy lzae frca ksvy" 

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = enviar_correo
        msg['Subject'] = "Confirmación de Cita"

        body = f"""
        Estimado/a {paciente_nombre},

        Su cita ha sido registrada con éxito.

        Doctor: {nombre_doctor}
        Fecha: {cita_fecha}
        Hora: {cita_hora}

       ¡Feliz Día!
        """
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            QMessageBox.information(self, "Éxito", "Cita registrada y correo de confirmación enviado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo enviar el correo: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Citas()
    form.show()
    sys.exit(app.exec_())