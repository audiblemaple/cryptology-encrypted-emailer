import asyncio
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
    QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread
from BlowFish import blowfish
import base64
import websockets
from EccElGamal import elgamal_class


class WebSocketWorker(QObject):
    finished = pyqtSignal()
    messageReceived = pyqtSignal(str)

    @pyqtSlot(str)
    async def send_message(self, message):
        uri = "ws://localhost:6789"
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
            print(f"> {message}")

            greeting = await websocket.recv()
            print(f"< {greeting}")
            self.messageReceived.emit(greeting)
        self.finished.emit()


class EmailSenderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.thread = QThread()
        self.worker = WebSocketWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(lambda: asyncio.run(
            self.worker.send_message(self.encrypt_text_with_blowfish(self.bodyTextEdit.toPlainText()))))
        self.worker.finished.connect(self.thread.quit)
        self.worker.messageReceived.connect(self.onMessageReceived)

    def initUI(self):
        # Set the window properties
        self.setWindowTitle('Email Sender')
        self.setGeometry(100, 100, 400, 300)

        # Create a vertical layout for the main window
        mainLayout = QVBoxLayout()

        # Add widgets to the layout
        self.toLabel = QLabel('To:')
        self.toLineEdit = QLineEdit()
        self.subjectLabel = QLabel('Subject:')
        self.subjectLineEdit = QLineEdit()
        self.bodyLabel = QLabel('Body:')
        self.bodyTextEdit = QTextEdit()

        # Create a horizontal layout for the button
        buttonLayout = QHBoxLayout()
        self.sendButton = QPushButton('Send Email')
        self.sendButton.clicked.connect(self.sendEmail)
        self.sendButton.setFixedWidth(200)

        # Add stretch to both sides of the button to center it
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.sendButton)
        buttonLayout.addStretch()

        # Add widgets and layouts to the main layout
        mainLayout.addWidget(self.toLabel)
        mainLayout.addWidget(self.toLineEdit)
        mainLayout.addWidget(self.subjectLabel)
        mainLayout.addWidget(self.subjectLineEdit)
        mainLayout.addWidget(self.bodyLabel)
        mainLayout.addWidget(self.bodyTextEdit)
        mainLayout.addLayout(buttonLayout)  # Add the button layout

        blowfish.init()
        encrypt_key()

        # Set the layout on the application's window
        self.setLayout(mainLayout)



    def sendEmail(self):
        print("Starting email sending process...")
        plaintext = self.bodyTextEdit.toPlainText()
        encrypted = blowfish.encrypt_text_with_blowfish(plaintext)
        print("Encrypted:", encrypted)

        # Start the thread to send the message asynchronously
        if not self.thread.isRunning():
            self.thread.start()

    def onMessageReceived(self, encoded_message):
        try:
            # Decode the message from Base64
            message = base64.b64decode(encoded_message)
            decrypted = blowfish.decrypt_text_with_blowfish(message)
            print("Decrypted:", decrypted)
        except Exception as e:
            print(f"Error processing received message: {e}")


def key_to_int(key):
    return int.from_bytes(key, 'big')


def int_to_key(integer, key_size=56):
    # The number of bytes is the key_size. The 'big' argument specifies the byte order.
    return integer.to_bytes(key_size, 'big')

def encrypt_key():
    print("Encrypting blowfish key")
    print("Original key: ", blowfish.key_as_int())

    ecc = elgamal_class.ElgamalEncryption()
    C1x, C1y, C2x, C2y = ecc.encrypt(blowfish.key_as_int())
    print("Decrypted key:", ecc.decrypt(C1x, C1y, C2x, C2y))
    return C1x, C1y, C2x, C2y


def main():
    app = QApplication(sys.argv)

    # Simulate some load time
    app.processEvents()

    window = EmailSenderGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
















    # def pkcs7_pad(self, data, block_size):
    #     padding_len = block_size - (len(data) % block_size)
    #     padding = bytes([padding_len] * padding_len)
    #     return data + padding
    #
    # def pkcs7_unpad(self, data):
    #     padding_len = data[-1]
    #     if padding_len > len(data):
    #         raise ValueError("Invalid padding")
    #     return data[:-padding_len]

    # def encrypt_text_with_blowfish(self, text):
    #     text_bytes = text.encode('utf-8')
    #     padded_text_bytes = self.pkcs7_pad(text_bytes, 8)  # Blowfish block size is 8 bytes
    #     # Apply padding here to make text_bytes a multiple of 8 bytes if necessary
    #
    #     encrypted_blocks = []
    #     for i in range(0, len(padded_text_bytes), 8):
    #         block = padded_text_bytes[i:i + 8]
    #         block_int = int.from_bytes(block, byteorder='big')
    #         encrypted_block_int = blowfish.encrypt(block_int)
    #         encrypted_blocks.append(encrypted_block_int.to_bytes(8, byteorder='big'))
    #
    #
    #     print("OG key as bytes:\n", blowfish.key)
    #     print("bytes key as int:\n", blowfish.key_as_int())
    #
    #     ecc = elgamal_class.ElgamalEncryption()
    #     C1x, C1y, C2x, C2y = ecc.encrypt(blowfish.key_as_int())
    #     print("decrypted key as bytes:\n", int_to_key(ecc.decrypt(C1x, C1y, C2x, C2y)))
    #
    #
    #
    #     encrypted_data = b''.join(encrypted_blocks)
    #     encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
    #     return encrypted_base64

    # def decrypt_text_with_blowfish(self, encrypted_base64):
    #     encrypted_data = base64.b64decode(encrypted_base64)
    #     decrypted_blocks = []
    #     for i in range(0, len(encrypted_data), 8):
    #         block = encrypted_data[i:i + 8]
    #         block_int = int.from_bytes(block, byteorder='big')
    #         decrypted_block_int = blowfish.decrypt(block_int)
    #         decrypted_blocks.append(decrypted_block_int.to_bytes(8, byteorder='big'))
    #
    #     decrypted_data = b''.join(decrypted_blocks)
    #     decrypted_data = self.pkcs7_unpad(decrypted_data)
    #     return decrypted_data.decode('utf-8')