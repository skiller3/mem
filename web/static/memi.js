(function() {

    let outputTerminal = new Terminal();
    let inputTerminal = new Terminal();
    
    let displayMessage = false;
    let memlistOutput = '';
    let memcmdOutput = '';
    let command = '';

    window.onload = function() {
        outputTerminal.open(document.getElementById('output-terminal'));
        
        // Hide cursor
        outputTerminal.write('\033[?25l');

        inputTerminal.open(document.getElementById('input-terminal'));
        inputTerminal.write("mem> ")
        inputTerminal.onData(handleUserInput);
        inputTerminal.focus();

        loadMemlistOutput();
        setInterval(loadMemlistOutput, 2000);
    }

    function handleUserInput(key) {
        if (displayMessage) {
            displayMessage = false;
            setTimeout(displayOutputTerminalContent, 0);
            return;
        }

        switch (key) {
            case '\r':               // Enter
                runMemcmd();
                command = '';
                inputTerminal.reset()
                // Clear terminal
                // inputTerminal.write("\033[3J")
                inputTerminal.write("mem> ")
                break;
            case '\u007F':           // Backspace (DEL)
                // Do not delete the prompt
                if (inputTerminal._core.buffer.x > 5) {
                    inputTerminal.write('\b \b');
                    if (command.length > 0) {
                        command = command.substr(0, command.length - 1);
                    }
                }
                break;
            default:                 // Print all other characters for demo
                if (key >= String.fromCharCode(0x20) && key <= String.fromCharCode(0x7E) || key >= '\u00a0') {
                    command += key;
                    inputTerminal.write(key);
                }
        }
    }

    function displayOutputTerminalContent() {
        outputTerminal.reset();

        // Hide cursor
        outputTerminal.write('\033[?25l');

        if (displayMessage) {
            outputTerminal.write(memcmdOutput);
            outputTerminal.write("\n---------- PRESS ANY KEY TO CONTINUE ----------");
        }
        else {
            outputTerminal.write(memlistOutput);
        }
    }

    function loadMemlistOutput() {
        axios({
            method: 'get',
            url: '/memlist',
        }).then(function(resp) {
            memlistOutput = resp.data;
            displayOutputTerminalContent();
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
            memcmdOutput = resp.data;
            if (memcmdOutput.length > 0) {
                displayMessage = true;
            }
            displayOutputTerminalContent();
        })  
    }

})();