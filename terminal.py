from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# HTML Template for the Terminal
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebTerminal</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background-color: #1a1a1a; /* Darker background for better contrast */
            color: #00ff00;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding-top: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            background-color: #1a1a1a; /* Matching container background */
            border: 1px solid #00ff00; /* Green border to match theme */
        }
        h1 {
            text-align: center;
            font-size: 2.2em;
            margin-bottom: 20px;
            color: #00ff00;
        }
        #terminal {
            background-color: #000000; /* Black terminal background */
            border: 1px solid #00ff00; /* Green border to match theme */
            border-radius: 5px;
            padding: 15px;
            min-height: 400px;
            overflow-y: auto;
            white-space: pre;
        }
        #output {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        #input-line {
            display: flex;
            margin-top: 15px;
        }
        #prompt {
            color: #00ff00;
            margin-right: 10px;
        }
        #command-input {
            flex-grow: 1;
            background-color: transparent;
            border: none;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 1em;
            outline: none;
        }
        #command-input:focus {
            border-bottom: 2px solid #ff0000; /* Red input focus border */
        }
        form {
            margin: 0;
        }
        @media (max-width: 768px) {
            #terminal {
                font-size: 0.9em;
                padding: 10px;
            }
            h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container" role="main">
        <h1>WebTerminal</h1>
        <div id="terminal" aria-live="polite">
            <div id="output">{{ output }}</div>
            <form method="POST" id="command-form">
                <div id="input-line">
                    <span id="prompt" aria-hidden="true">user@webterminal:~$</span>
                    <input type="text" id="command-input" name="command" autocomplete="off" autofocus aria-label="Command Input">
                </div>
            </form>
        </div>
    </div>
    <script>
        document.getElementById('command-form').addEventListener('submit', function(e) {
            e.preventDefault();
            var command = document.getElementById('command-input').value;
            fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'command=' + encodeURIComponent(command)
            })
            .then(response => response.text())
            .then(html => {
                var parser = new DOMParser();
                var doc = parser.parseFromString(html, 'text/html');
                var newOutput = doc.getElementById('output').innerHTML; // Get updated output
                document.getElementById('output').innerHTML = newOutput; // Update only the output div
                document.getElementById('command-input').value = ''; // Clear the input field
            });
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def terminal():
    output = ''
    if request.method == 'POST':
        command = request.form['command']
        if command.lower() == 'help':
            output = "Available commands:\n- echo: Display a line of text\n- help: Display this help message\n"
        elif command.lower().startswith('echo'):
            output = command[5:] + "\n"
        else:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
                output = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                output = "Command execution timed out.\n"
            except Exception as e:
                output = f"An error occurred: {str(e)}\n"
        
        output = f"user@webterminal:~$ {command}\n{output}"
    
    return render_template_string(html_template, output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=19506)
