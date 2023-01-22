(function() {

    let outputTerminal = null;
    let inputTerminal = null;
    
    let messageMode = false;
    let outputTerminalText = '';
    let command = '';

    let editActions = [
        'edit-focus-target-description',
        'edit',
        'ed',
        'e'
    ];

    function onDocumentReady(fn) {
        if (document.readyState != 'loading'){
            fn();
            return;
        }
        document.addEventListener('DOMContentLoaded', fn);
    }

    onDocumentReady(function() {
        let fontSize = window.innerHeight * 2 / 100;  // Equivalent to 1.5vw

        outputTerminal = new Terminal({fontSize, convertEol: true});
        inputTerminal = new Terminal({fontSize, convertEol: true});

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
        });
    });

    function handleUserInput(key) {
        if (messageMode) {
            messageMode = false;
            setTimeout(loadMemlistOutput, 0);
            return;
        }

        switch (key) {
            case '\r':  // Enter
                command = command.trim();
                commandFrags = command.split(/\s+/);
                if (command.toLowerCase() === 'q' || command.toLowerCase() === 'quit') {
                    window.open(document.URL, "_self");
                }
                else if (commandFrags.length === 2 && editActions.includes(commandFrags[0].toLowerCase())) {
                    window.open(`/static/edit.html?focusitem=${commandFrags[1]}`, "_blank");
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

})();