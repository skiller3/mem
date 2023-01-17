(function() {

    let fontSize = getWidth() >= 1201 ? 16 : 32;
    let outputTerminal = new Terminal({fontSize, convertEol: true});
    let inputTerminal = new Terminal({fontSize, convertEol: true});
    
    let messageMode = false;
    let outputTerminalText = '';
    let command = '';

    window.onload = function() {
        outputTerminal.open(document.getElementById('output-terminal'));
        // Hide cursor in output terminal
        outputTerminal.write('\033[?25l');

        inputTerminal.open(document.getElementById('input-terminal'));
        inputTerminal.write("mem> ")
        inputTerminal.onData(handleUserInput);
        inputTerminal.focus();

        loadMemlistOutput();
        setInterval(loadMemlistOutput, 2000);

        let inputTerminalEl = document.querySelector("#input-terminal > .terminal");
        inputTerminalEl.addEventListener("focusout", () => setTimeout(() => inputTerminal.focus()));
        setInterval(() => inputTerminal.focus(), 200);

        setTimeout(() => {
            let textareaEl = document.querySelector("#input-terminal textarea");
            textareaEl.setAttribute("inputmode", "email");
            textareaEl.click();
            window.alert("armed")
        });
    }

    function handleUserInput(key) {
        if (messageMode) {
            messageMode = false;
            setTimeout(loadMemlistOutput, 0);
            return;
        }

        switch (key) {
            case '\r':  // Enter
                command = command.trim();
                if (command.toLowerCase() === 'q' || command.toLowerCase() === 'quit') {
                    logout();
                }
                else if (command !== '') {
                    runMemcmd();
                }
                command = '';
                inputTerminal.reset()
                inputTerminal.write("mem> ")
                break;
            case '\u007F':  // Backspace (DEL)
                // Do not delete the prompt
                if (inputTerminal._core.buffer.x > 5) {
                    inputTerminal.write('\b \b');
                    if (command.length > 0) {
                        command = command.substr(0, command.length - 1);
                    }
                }
                break;
            case ':':
                autocomplete();
                break;
            case '@':
                autocomplete();
                break;
            case '\t':
                autocomplete();
                break;
            default:  // Print other characters to match the demo at https://xtermjs.org/
                if (key >= String.fromCharCode(0x20) && key <= String.fromCharCode(0x7E) || key >= '\u00a0') {
                    command += key;
                    inputTerminal.write(key);
                }
        }
    }

    function displayMemlistOutput(text) {
        if (messageMode) {
            return;
        }
        if (outputTerminalText === text) {
            return;
        }
        outputTerminalText = text;
        outputTerminal.reset();
        // Hide cursor in output terminal
        outputTerminal.write('\033[?25l');
        outputTerminal.write(outputTerminalText)
    }

    function displayMessage(text) {
        if (text.length < 1) {
            return;
        }
        messageMode = true;
        outputTerminalText = text;
        outputTerminalText += "\n-------- PRESS ANY KEY TO CONTINUE --------"
        outputTerminal.reset();
        // Hide cursor in output terminal
        outputTerminal.write('\033[?25l');
        outputTerminal.write(outputTerminalText);
    }

    function loadMemlistOutput() {
        axios({
            method: 'get',
            url: '/memlist',
        }).then(function(resp) {
            displayMemlistOutput(resp.data)
        })
    }

    function runMemcmd() {
        axios({
            method: 'post',
            url: '/memcmd',
            data: {
                command: command
            }
        }).then(function(resp) {
            displayMessage(resp.data);
        })  
    }

    function autocomplete() {
        axios({
            method: 'post',
            url: '/autocomplete',
            data: {
                command: command
            }
        }).then(function(resp) {
            command = resp.data;
            inputTerminal.reset()
            inputTerminal.write("mem> ")
            inputTerminal.write(command)
        });
    }

    function logout() {
        axios({
            method: 'post',
            url: '/logout'
        }).then(function(resp) {
            window.open("/", "_self")
        });
    }

    function getWidth() {
        if (window.innerWidth) {
          return window.innerWidth;
        }
        if (document.documentElement && document.documentElement.clientWidth) {
          return document.documentElement.clientWidth;
        }
        if (document.body) {
          return document.body.clientWidth;
        }
      }

})();