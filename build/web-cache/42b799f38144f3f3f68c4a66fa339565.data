"use strict";

/*  BF2 is still broken see  https://github.com/jvilk/BrowserFS/issues/325
import { configure, BFSRequire, EmscriptenFS } from './browserfs.mjs';
//import { Buffer } from 'buffer';

window.BrowserFS = {}
window.BrowserFS.configure = configure
window.BrowserFS.BFSRequire = BFSRequire
window.BrowserFS.EmscriptenFS = EmscriptenFS
window.BrowserFS.Buffer = BFSRequire('buffer')
*/
var bfs2 = false

async function import_browserfs() {
    console.warn("late import", config.cdn+"browserfs.min.js" )
    var script = document.createElement("script")
    script.src = vm.config.cdn + "browserfs.min.js"
    document.head.appendChild(script)
    await _until(defined)("BrowserFS")
}


/*  Facilities implemented in js

    js.SVG     : convert svg to png
    js.FETCH   : async GET/POST via fetch
    js.MM      : media manager
        js.MM.CAMERA
    js.VT      : terminal creation
    js.FTDI    : usb serial
    js.MISC    : todo

*/

const module_name = "pythons.js"


var config


const FETCH_FLAGS = {
    mode:"no-cors",
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    credentials: 'omit'
}


window.get_terminal_cols = function () {
    var cdefault = vm.config.cols || 132
    const cols = (window.terminal && terminal.dataset.cols) || cdefault
    return Number(cols)
}

window.get_terminal_console = function () {
    var cdefault = 0
    if (window.terminal)
        if (vm && vm.config.debug)
            cdefault = 10
    return Number( (window.terminal && terminal.dataset.console) || cdefault )
}

window.get_terminal_lines = function () {
    return Number( (window.terminal && terminal.dataset.lines) || vm.config.lines) + get_terminal_console()
}


if (window.config) {
   config = window.config
} else {
   config = {}
}

if (document.characterSet.toLowerCase() !== "utf-8")
    alert("Host page encoding must be set to UTF-8 with tag :  meta charset=utf-8")

window.addEventListener("error", function (e) {
   alert("Error occurred: " + e.error.message);
   return false;
})

window.addEventListener('unhandledrejection', function (e) {
  alert("Error occurred: " + e.reason.message);
})

function reverse(s){
    return s.split("").reverse().join("");
}

// please comment here if you find a bug
// https://stackoverflow.com/questions/5202085/javascript-equivalent-of-pythons-rsplit

String.prototype.rsplit = function(sep, maxsplit) {
    var result = []
    if ( (sep === undefined) ) {
        sep = " "
        maxsplit = 0
    }

    if (maxsplit === 0  )
        return [this]

    var data = this.split(sep)


    if (!maxsplit || (maxsplit<0) || (data.length==maxsplit+1) )
        return data

    while (data.length && (result.length < maxsplit)) {
        result.push( data.pop() )
    }
    if (result.length) {
        result.reverse()
        if (data.length>1) {
            // thx @imkzh
            return [data.join(sep), ...result ]
        }
        return result
    }
    return [this]
}


function jsimport(url, sync) {
    const jsloader=document.createElement('script')
    jsloader.setAttribute("type","text/javascript")
    jsloader.setAttribute("src", url)
    if (!sync)
        jsloader.setAttribute('async', true);
    document.head.appendChild(jsloader)
}
window.jsimport = jsimport

window.__defineGetter__('__FILE__', function() {
  return (new Error).stack.split('/').slice(-1).join().split('?')[0].split(':')[0] +": "
})


const delay = (ms, fn_solver) => new Promise(resolve => setTimeout(() => resolve(fn_solver()), ms));


function _until(fn_solver){
    return async function fwrapper(){
        var argv = Array.from(arguments)
        function solve_me(){return  fn_solver.apply(window, argv ) }
        while (!await delay(16, solve_me ) )
            {};
    }
}
window._until =  _until

function defined(e, o) {
    if (typeof o === 'undefined' || o === null)
        o = window;
    try {
        e = o[e];
    } catch (x) { return false }

    if (typeof e === 'undefined' || e === null)
        return false;
    return true;
}
window.defined = defined

// promise to iterator converter
var prom = {}
var prom_count = 0
window.iterator = function * iterator(oprom) {
    if (prom_count > 32000 ) {
        console.warn("resetting prom counter")
        prom_count = 0
    }

    const mark = prom_count++;
    var counter = 0;
    oprom.then( (value) => prom[mark] = value )
    while (!prom[mark]) {
        yield counter++;
    }
    yield prom[mark];
    delete prom[mark]
}


window.checkStatus = function checkStatus(response) {
    if (!response.ok) {
        response.error =  new Error(`HTTP ${response.status} - ${response.statusText}`);
        return null
    }
    return response;
}


window.addEventListener('unhandledrejection', function(event) {
  console.error("uncaught :",event.promise); // the promise that generated the error
  console.error("uncaught :",event.reason); // the unhandled error object
})


//fileretrieve (binary). TODO: wasm compilation
window.cross_file = function * cross_file(url, store, flags) {
    cross_file.dlcomplete = 1
    var content = 0
    var response = null
    console.log("Begin.cross_file.fetch", url, flags || FETCH_FLAGS )

    fetch(url, flags || FETCH_FLAGS)
        .then( resp => {
                response = resp
                console.log("cross_file.fetch", response.status)
                if (checkStatus(resp))
                    return response.arrayBuffer()
                else {
                    console.warn("got wrong status", response)
                }
            })
        .then( buffer => content = new Uint8Array(buffer) )
        .catch(x => {
                response = { "error" : new Error(x) }
            })

    while (!response)
        yield content

    while (!content && !response.error )
        yield content

    if (response.error) {
        console.warn("cross_file.error :", response.error)
        return response.error
    } else {
        // console.warn("got response", response, "len", response.headers.get("Content-Length"))
    }
    FS.writeFile(store, content )
    console.log("End.cross_file.fetch", store, "r/w=", content.byteLength)
    cross_file.dlcomplete = content.byteLength
    yield store
}




window.cross_dl = async function cross_dl(url, flags) {
    console.log("cross_dl.fetch", url, flags || FETCH_FLAGS )
    const response = await fetch(url, flags || FETCH_FLAGS )
    checkStatus(response)
    console.log("cross_dl len=", response.headers.get("Content-Length") )
    console.log("cross_dl.error", response.error )
    if (response.body) {
        return await response.text()
    } else {
        console.error("cross_dl: no body")
    }
    return ""
}





//urlretrieve
function DEPRECATED_wget_sync(url, store){
    const request = new XMLHttpRequest();
    try {
        request.open('GET', url, false);
        request.send(null);
        if (request.status === 200) {
            console.log(`DEPRECATED_wget_sync(${url})`);
            FS.writeFile( store, request.responseText);
        }
        return request.status
    } catch (ex) {
        return 500;
    }
}

//https://stackoverflow.com/questions/326069/how-to-identify-if-a-webpage-is-being-loaded-inside-an-iframe-or-directly-into-t
function is_iframe() {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

function prerun(VM) {
    console.warn("VM.prerun")

    VM.FS = FS

/*
    if (window.BrowserFS) {
        VM.BFS = new BrowserFS.EmscriptenFS()
        VM.BFS.Buffer = BrowserFS.BFSRequire('buffer').Buffer
    } else {
        console.error("VM.prerun","BrowserFS not found")
    }
*/
    const sixel_prefix = String.fromCharCode(27)+"Pq"


    var buffer_stdout = ""
    var buffer_stderr = ""
    var flushed_stdout = false
    var flushed_stderr = false


    const text_codec = new TextDecoder()


    function b_utf8(s) {
        var ary = []
        for ( var i=0; i<s.length; i+=1 ) {
            ary.push( s.substr(i,1).charCodeAt(0) )
        }
        return text_codec.decode(  new Uint8Array(ary) )
    }


    function stdin() {
        return null
    }


    function stdout(code) {

        var flush = (code == 4)

        if (flush) {
            flushed_stdout = true
        } else {
            if (code == 10) {
                if (flushed_stdout) {
                    flushed_stdout = false
                    return
                }

                buffer_stdout += "\r\n";
                flush = true
            }
            flushed_stdout = false
        }

        if (buffer_stdout != "") {
            if (flush) {
                if (buffer_stdout.startsWith(sixel_prefix)) {
                    console.info("[sixel image]");
                    VM.vt.sixel(buffer_stdout);
                } else {
                    if (buffer_stdout.startsWith("Looks like you are rendering"))
                        return;

                    VM.vt.xterm.write( b_utf8(buffer_stdout) )
                }
                buffer_stdout = ""
                return
            }
        }
        if (!flush)
            buffer_stdout += String.fromCharCode(code);
    }


    function stderr(code) {
        var flush = (code == 4)

        if (flush) {
            flushed_stderr = true
        } else {
            if (code === 10) {
                if (flushed_stderr) {
                    flushed_stderr = false
                    return
                }
                buffer_stderr += "\r\n";
                flush = true
            }
            flushed_stderr = false
        }

        if (buffer_stderr != "") {
            if (flush) {
                if (!VM.vt.nodup)
                    console.log(buffer_stderr);

                VM.vt.xterm.write( b_utf8(buffer_stderr) )
                buffer_stderr = ""
                return
            }
        }
        if (!flush)
            buffer_stderr += String.fromCharCode(code);
    }

    // put script namespace in sys.argv[0]
    // default is org.python
    VM.arguments.push(VM.APK)

    VM.FS.init(stdin, stdout, stderr);

}


const vm = {
        APK : "org.python",

        arguments: [],

        cpy_argv : [],
        sys_argv : [],

        script : {},

        is_ready : 0,

        DEPRECATED_wget_sync : DEPRECATED_wget_sync,

        vt : {
                xterm : { write : console.log},
                sixel : function(data){ vm.vt.xterm.write(`[sixel:${data && data.length}]\r\n`)},
                nodup : 1
        },

//        canvas: (() => document.getElementById('canvas'))(),

        setStatus : function(text) {
            const statusElement = document.getElementById('status') || {}
            const progressElement = document.getElementById('progress') || {};
            const spinnerElement = document.getElementById('spinner') || { style: {} } ;

            if (text == "hide") {
                progressElement.value = null;
                progressElement.max = null;
                progressElement.hidden = true;
                spinnerElement.style.display = 'none';
                statusElement.innerHTML = "";
                return ;
            }

            if (!this.setStatus.last)
                this.setStatus.last = { time: Date.now(), text: '' };

            if (text === this.setStatus.last.text)
                return;

            var m = text.match(/([^(]+)\((\d+(\.\d+)?)\/(\d+)\)/);
            var now = Date.now();
            if (m && now - this.setStatus.last.time < 30)
                return; // if this is a progress update, skip it if too soon
            this.setStatus.last.time = now;
            this.setStatus.last.text = text;
            if (m) {
                text = m[1];
                progressElement.value = ( parseInt(m[2]) / parseInt(m[4]) ) * 100;
                if (progressElement.value>95) {
                    if (progressElement.max>100) {
//TODO: replace by real download progress on .data and wasm instanciation stats.
                        setTimeout( ()=>{ progressElement.value=125 } , 2000)
                        setTimeout( ()=>{ progressElement.value=150 } , 5000)
                        setTimeout( ()=>{ progressElement.value=190 } , 7000)
                    }
                }
                progressElement.hidden = false;
                spinnerElement.hidden = false;
            } else {
                progressElement.value = null;
                progressElement.max = null;
                progressElement.hidden = true;
                if (!text)
                    spinnerElement.style.display = 'none';
            }
            statusElement.innerHTML = text;
        },

        locateFile : function(path, prefix) {
            if (path == "main.data") {
                const url = (config.cdn || "" )+`python${config.pydigits}/${path}`
                console.log(__FILE__,"locateData: "+path+' '+prefix, "->", url);
                return url;
            } else {
                console.log(__FILE__,"locateFile: "+path+' '+prefix);
            }
            return prefix + path;
        },

        PyRun_SimpleString : function(code) {
            const ud = { "type" : "rcon", "data" : code }
            if (window.worker) {
                window.worker.postMessage({ target: 'custom', userData: ud });
            } else {
                this.postMessage(ud);
            }
        },

        readline : function(line) {
            const ud = { "type" : "stdin", "data" : line }
            if (window.worker) {
                //if (line.search(chr(0x1b)))
                  //  console.log("446: non-printable", line)
                window.worker.postMessage({ target: 'custom', userData: ud });
            } else {
                this.postMessage(ud);
            }
        },

        rawstdin : function (char) {
            const ud = { "type" : "raw", "data" : char }
            if (window.worker) {
                window.worker.postMessage({ target: 'custom', userData: ud });
            } else {
                this.postMessage(ud);
            }
        },

        websocket : { "url" : "wss://" },
        preRun : [ prerun ],
        postRun : [ function (VM) {
            window.VM = VM
            window.python = VM
            window.py = new bridge(VM)
            setTimeout(custom_postrun, 10)
        }]
}


async function run_pyrc(content) {
    const pyrc_file = "/data/data/org.python/assets/pythonrc.py"
    const main_file = "/data/data/org.python/assets/main.py"

    vm.FS.writeFile(pyrc_file, content )

// embedded canvas
    if (vm.PyConfig.frozen) {
        if ( canvas.dataset.path ) {
            vm.PyConfig.frozen_path = canvas.dataset.src
        } else {
            vm.PyConfig.frozen_path = location.href.rsplit("/",1)  // current doc url as base
        }
        var frozencode = canvas.innerHTML
        if (canvas.dataset.embed) {
            vm.PyConfig.frozen_handler = canvas.dataset.embed
        }
        FS.writeFile(vm.PyConfig.frozen, frozencode)
    } else {
// TODO: concat blocks
        vm.FS.writeFile(main_file, vm.script.blocks[0] )
    }

    python.PyRun_SimpleString(`#!site
import os, sys, json
PyConfig = json.loads("""${JSON.stringify(python.PyConfig)}""")
pfx=PyConfig['prefix']
def os_path_is_dir(path):
    try:
        os.listdir(str(path))
        return True
    except:
        return False
def os_path_is_file(path):
    parent, file = str(path).rsplit('/',1)
    try:
        return file in os.listdir(parent)
    except:
        return False

if os_path_is_dir(pfx):
    sys.path.append(pfx)
    os.chdir(pfx)

print("581: Current Dir :", pfx)
del pfx
__pythonrc__ = "${pyrc_file}"
try:
    if os_path_is_file(__pythonrc__):
        exec(open(__pythonrc__).read(), globals(), globals())
    else:
        raise Error("File not found")
except Exception as e:
    print(f"579: invalid {__pythonrc__=}")
    sys.print_exception(e)

try:
    import asyncio
    asyncio.run(import_site("${main_file}"))
except ImportError:
    pass
`)
}


function store_file(url, local) {
    fetch(url, {})
        .then( response => checkStatus(response) && response.arrayBuffer() )
        .then( buffer => vm.FS.writeFile(local, new Uint8Array(buffer)) )
        .catch(x => console.error(x))
}
async function custom_postrun() {
    console.warn("VM.postrun Begin")
    const pyrc_url = vm.config.cdn + "pythonrc.py"
    var content = 0

    fetch(pyrc_url, {})
        .then( response => checkStatus(response) && response.arrayBuffer() )
        .then( buffer => run_pyrc(new Uint8Array(buffer)) )
        .catch(x => console.error(x))

    console.warn("VM.postrun End")
}


// ===================== DOM features ====================



function feat_gui(debug_hidden) {

    var canvas2d = document.getElementById("canvas")

    function add_canvas(name, width, height) {
        const new_canvas = document.createElement("canvas")
        new_canvas.id = name
        new_canvas.width = width || 1
        new_canvas.height = height || 1
        document.body.appendChild(new_canvas)
        return new_canvas
    }



    if (!canvas2d) {
        canvas2d =  add_canvas("canvas")
        canvas2d.style.position = "absolute"
        canvas2d.style.top = "0px"
        canvas2d.style.right = "0px"
        canvas2d.tabindex = 0
        //var ctx = canvas.getContext("2d")
    } else {
        // user managed canvas
console.warn("TODO: user defined canvas")
    }

    config.user_canvas = config.user_canvas || 0 //??=
    config.user_canvas_managed = config.user_canvas_managed || 0 //??=

    vm.canvas2d = canvas2d

    var canvas3d = document.getElementById("canvas3d")
    if (!canvas3d) {
        canvas3d = add_canvas("canvas3d", 128, 128)
        canvas3d.style.position = "absolute"
        canvas3d.style.bottom = "0px"
        canvas3d.style.left = "0px"

    }
    vm.canvas3d = canvas3d


    canvas.addEventListener("click", MM.focus_handler)
/*



    function event_fullscreen(event){
        if (!event.target.hasAttribute('fullscreen')) return;
        if (document.fullscreenElement) {
            document.exitFullscreen()
        } else {
            document.documentElement.requestFullscreen()
        }
    }
    document.addEventListener('click', event_fullscreen, false);

*/

    // window resize
    function window_canvas_adjust(divider) {
        const canvas = vm.canvas2d
        var want_w
        var want_h

        const ar = canvas.width / canvas.height

        // default is maximize
        var max_width = window.innerWidth
        var max_height = window.innerHeight


        if (vm.config.debug) {
            max_width = max_width * .80
            max_height = max_height * .80
        } else {
            // max_height -= 150
        }

        want_w = max_width
        want_h = max_height


        if (window.devicePixelRatio != 1 )
            console.warn("Unsupported device pixel ratio", window.devicePixelRatio)

        if (vm.config.debug) {
            divider = vm.config.gui_debug
        } else {
            divider = vm.config.gui_divider || 1
        }


        if (vm.config.debug)
            console.log("window[DEBUG]:", want_w, want_h, ar, divider)

        want_w = Math.trunc(want_w / divider )
        want_h = Math.trunc(want_w / ar)


        // constraints
        if (want_h > max_height) {
            if (vm.config.debug)
                console.warn("too tall : have",max_height,"want",want_h)
            want_h = max_height
            want_w = want_h * ar
        }

        if (want_w > max_width) {
            if (vm.config.debug)
                console.warn("too wide : have",max_width,"want",want_w)
            want_w = max_width
            want_h = want_h / ar
        }


        if (vm.config.debug) {
            canvas.style.margin= "none"
            canvas.style.left = "auto"
            canvas.style.bottom = "auto"
        } else {
            // canvas position is handled by program
            if (vm.config.user_canvas)
                return

            // center canvas
            canvas.style.position = "absolute"
            canvas.style.left = 0
            canvas.style.bottom = 0
            canvas.style.top = 0
            canvas.style.right = 0
            canvas.style.margin= "auto"
        }

        // apply
        canvas.style.width = want_w + "px"
        canvas.style.height = want_h + "px"

        if (vm.config.debug)
            console.log(`window[DEBUG:CORRECTED]: ${want_w}, ${want_h}, ar=${ar}, div=${divider}`)


    }


    function window_canvas_adjust_3d(divider) {
        const canvas = vm.canvas3d
        divider = divider || 1
        if ( (canvas.width==1) && (canvas.height==1) ){
            console.log("canvas context not set yet")
            setTimeout(window_canvas_adjust_3d, 100, divider);
            return;
        }

        if (!vm.config.fb_ar) {
            vm.config.fb_width = canvas.width
            vm.config.fb_height = canvas.height
            vm.config.fb_ar  =  canvas.width / canvas.height
        }


        var want_w
        var want_h

        const ar = vm.config.fb_ar

        const dpr = window.devicePixelRatio
        if (dpr != 1 )
            console.warn("Unsupported device pixel ratio", dpr)

        // default is maximize
        // default is maximize
        var max_width = window.document.body.clientWidth
        var max_height = window.document.body.clientHeight
        want_w = max_width
        want_h = max_height


        if (vm.config.debug)
            console.log("window3D[DEBUG:CORRECTED]:", want_w, want_h, ar, divider)

        // keep fb ratio
        want_w = Math.trunc(want_w / divider )
        want_h = Math.trunc(want_w / ar)

        // constraints
        if (want_h > max_height) {
            //console.warn ("Too much H")
            want_h = max_height
            want_w = want_h * ar
        }

        if (want_w > max_width) {
            //console.warn("Too much W")
            want_w = max_width
            want_h = want_h / ar
        }

        // restore phy size
        canvas.width  = vm.config.fb_width
        canvas.height = vm.config.fb_height

        canvas.style.position = "absolute"
        canvas.style.top = 0
        canvas.style.right = 0

        if (!vm.config.debug) {
            // center canvas
            canvas.style.left = 0
            canvas.style.bottom = 0
            canvas.style.margin= "auto"
        } else {
            canvas.style.margin= "none"
            canvas.style.left = "auto"
            canvas.style.bottom = "auto"
        }

        // apply viewport size
        canvas.style.width = want_w + "px"
        canvas.style.height = want_h + "px"

        queue_event("resize3d", { width : want_w, height : want_h } )

    }

    function window_resize_3d(gui_divider) {
console.log(" @@@@@@@@@@@@@@@@@@@@@@ 3D CANVAS @@@@@@@@@@@@@@@@@@@@@@")
        setTimeout(window_canvas_adjust_3d, 200, gui_divider);
        setTimeout(window.focus, 300);
    }

    function window_resize_2d(gui_divider) {
        // don't interfere if program want to handle canvas placing/resizing
        if (vm.config.user_canvas_managed)
            return vm.config.user_canvas_managed

        if (!window.canvas) {
            console.warn("777: No canvas defined")
            return
        }

        setTimeout(window_canvas_adjust, 200, gui_divider);
        setTimeout(window.focus, 300);
    }



    function window_resize_event() {
        // special management for 3D ctx
        if (vm.config.user_canvas_managed==3) {
            window_resize(vm.config.gui_divider)
            return
        }
        window_resize(vm.config.gui_divider)
    }

    window.addEventListener('resize', window_resize_event);
    if (vm.config.user_canvas_managed==3)
        window.window_resize = window_resize_3d
    else
        window.window_resize = window_resize_2d

    vm.canvas = canvas2d || canvas3d
    return vm.canvas
}



// file transfer (upload)

async function feat_fs(debug_hidden) {
    var uploaded_file_count = 0

    if (!window.BrowserFS) {
        await import_browserfs()
    }

    function readFileAsArrayBuffer(file, success, error) {
        var fr = new FileReader();
        fr.addEventListener('error', error, false);
        if (fr.readAsBinaryString) {
            fr.addEventListener('load', function () {
                var string = this.resultString != null ? this.resultString : this.result;
                var result = new Uint8Array(string.length);
                for (var i = 0; i < string.length; i++) {
                    result[i] = string.charCodeAt(i);
                }
                success(result.buffer);
            }, false);
            return fr.readAsBinaryString(file);
        } else {
            fr.addEventListener('load', function () {
                success(this.result);
            }, false);
            return fr.readAsArrayBuffer(file);
        }
    }

    async function transfer_uploads(){
        //let reader = new FileReader();

        for (var i=0;i<dlg_multifile.files.length;i++) {
            let file = dlg_multifile.files[i]
            const datapath = `/tmp/upload-${uploaded_file_count}`
            var frec = {}
                frec["name"] = file.name
                frec["size"] = file.size
                frec["mimetype"] = file.type
                frec["text"] = datapath

            function file_done(data) {
                const pydata = JSON.stringify(frec)
                console.warn("UPLOAD", pydata );
                python.FS.writeFile(datapath, new Int8Array(data) )
                queue_event("upload", pydata )
            }
            readFileAsArrayBuffer(file, file_done, console.error )
            uploaded_file_count++;
        }

    }
    var dlg_multifile = document.getElementById("dlg_multifile")
    if (!dlg_multifile) {
        dlg_multifile = document.createElement('input')
        dlg_multifile.setAttribute("type","file")
        dlg_multifile.setAttribute("id","dlg_multifile")
        dlg_multifile.setAttribute("multiple",true)
        dlg_multifile.hidden = debug_hidden
        document.body.appendChild(dlg_multifile)
    }
    dlg_multifile.addEventListener("change", transfer_uploads );

}


// js.VT

// simpleterm
async function feat_vt(debug_hidden) {
    var stdio = document.getElementById('stdio')
    if (!stdio){
        stdio = document.createElement('div')
        stdio.id = "stdio"
        stdio.style.width = "640px";
        stdio.style.height = "480px";
        stdio.style.background = "black";
        stdio.style.color = "yellow";
        stdio.innerHTML = "vt100"
        stdio.hidden = debug_hidden
        stdio.setAttribute("tabIndex", 1)
        document.body.appendChild(stdio)
    }

    const { Terminal, helper, handlevt } = await import("./vt.js")

    vm.vt.xterm = new Terminal("stdio", get_terminal_cols(), get_terminal_lines())
    vm.vt.xterm.set_vm_handler(vm, null, null)

    vm.vt.xterm.open()

}

// xterm.js + sixel
async function feat_vtx(debug_hidden) {
    var terminal = document.getElementById('terminal')
    if (!terminal){
        terminal = document.createElement('div')
        terminal.id = "terminal"
        // if running apk only show wrt debug flag, default is hide
        if (vm.config.archive) {
            if (!vm.config.interactive)
                terminal.hidden = debug_hidden
        }

        terminal.style.zIndex = 0
        terminal.setAttribute("tabIndex", 1)
        document.body.appendChild(terminal)
    }

    const { WasmTerminal } = await import("./vtx.js")

    vm.vt = new WasmTerminal("terminal", get_terminal_cols(), get_terminal_lines(), [
            { url : (config.cdn || "./") + "xtermjsixel/xterm-addon-image-worker.js", sixelSupport:true}
    ] )
}


// simple <pre> output
function feat_stdout() {
    var stdout = document.getElementById('stdout')
    if (!stdout){
        stdout = document.createElement('pre')
        stdout.id = "stdout"
        stdout.style.whiteSpace = "pre-wrap"
        stdout.hidden = false
        document.body.appendChild(stdout)
    }
    stdout.write = function (text) {
        var buffer = stdout.innerHTML.split("\r\n")
        for (const line of text.split("\r\n") ) {
            if (line.length) {
                buffer.push( line )
            }
        }

        while (buffer.length>25)
            buffer.shift()

        stdout.innerHTML =  buffer.join("\n")

    }
    vm.vt.xterm = stdout
}

// TODO make a queue, python is not always ready to receive those events
// right after page load


function focus_handler(ev) {
    if (ev.type == "click") {
        canvas.removeEventListener("click", MM.focus_handler)
        canvas.focus()
        return
    }

    if (ev.type == "mouseenter") {
        canvas.focus()
        console.log("canvas focus set")
        if (MM.focus_lost && MM.current_trackid) {
            console.warn("resuming music queue")
            MM[MM.current_trackid].media.play()
        }

        canvas.removeEventListener("mouseenter", MM.focus_handler)
        return
    }

    if (ev.type == "focus") {
        queue_event("focus", ev )
        console.log("focus set")
        canvas.focus()
        return
    }

    // for autofocus
    if (ev.type == "blur") {
        // remove initial focuser that may still be there
        try {
            canvas.removeEventListener("click", MM.focus_handler)
        } catch (x ) {}

        canvas.addEventListener("click", MM.focus_handler)
        canvas.addEventListener("mouseenter", MM.focus_handler)
        queue_event("blur", ev )
        return
    }
}


function feat_lifecycle() {
        window.addEventListener("focus", MM.focus_handler)
        window.addEventListener("blur", MM.focus_handler)

        if (!vm.config.can_close) {
            window.onbeforeunload = function() {
                console.warn("window.onbeforeunload")
                if (MM.current_trackid) {
                    console.warn("pausing music queue")
                    MM.focus_lost = 1
                    MM[MM.current_trackid].media.pause()
                } else {
                    console.warn("not track playing")
                }
                const message = "Are you sure you want to navigate away from this page ?"
                if (confirm(message)) {
                    return message
                } else {
                    return false
                }
            }
        }
}


function feat_snd() {
    // to set user media engagement status and possibly make it blocking
    MM.UME = !vm.config.ume_block
    MM.is_safari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (!MM.UME && !MM.is_safari)
        MM_play( {auto:1, test:1, media: new Audio(config.cdn+"empty.ogg")} , 1)

    if (MM.is_safari) {
        MM.is_safari = function unlock_ume() {
                console.warn("safari ume unlocking")
                MM.UME = 1
                window.removeEventListener("click", MM.is_safari)
                MM.is_safari = 1
            }
        window.addEventListener("click", MM.is_safari)
    }
}

// ============================== event queue =============================

window.EQ = []


function queue_event(evname, data) {
    const jsdata = JSON.stringify(data)
    EQ.push( { name : evname, data : jsdata} )

    if (window.python && window.python.is_ready) {
        while (EQ.length>0) {
            const ev = EQ.shift()
            python.PyRun_SimpleString(`#!
__EMSCRIPTEN__.EventTarget.build('${ev.name}', '''${ev.data}''')
`)
        }
    } else {
        console.warn(`Event "${evname}" queued : too early`)
    }
}

// js.MM
// =============================  media manager ===========================

// js.MM.download
function download(diskfile, filename) {
    if (!filename)
        filename = diskfile.rsplit("/").pop()

    const blob = new Blob([FS.readFile(diskfile)])
    const elem = window.document.createElement('a');
    elem.href = window.URL.createObjectURL(blob, { oneTimeOnly: true });
    elem.download = filename;
    document.body.appendChild(elem);
    elem.click();
    document.body.removeChild(elem);
}



window.MM = {
    tracks : 0,
    trackid_current : 0,
    next : "",
    next_hint : "",
    next_loops : 0,
    next_tid : 0,
    transition : 0,
    UME : true,
    download : download,
    focus_lost : 0,
    focus_handler : focus_handler,
    camera : {}
}

async function media_prepare(trackid) {
    const track = MM[trackid]


    await _until(defined)("avail", track)

    if (track.type === "audio") {
        //console.log(`audio ${trackid}:${track.url} ready`)
        return
    }

    if (track.type === "fs") {
        console.log(`fs ${trackid}:${track.url} => ${track.path} ready`)
        return
    }


    if (track.type === "mount") {

        if (!vm.BFS) {
            await import_browserfs()

            // how is passed the FS object ???
            vm.BFS = new BrowserFS.EmscriptenFS()  // {FS:vm.FS}

            vm.BFS.Buffer = BrowserFS.BFSRequire('buffer').Buffer
        }

        // async
        MM[trackid].media = await vm.BFS.Buffer.from( MM[trackid].data )

        track.mount.path = track.mount.path || '/' //??=

        const hint = `${track.mount.path}@${track.mount.point}:${trackid}`

        if (!vm.BFS) {
            // how is passed the FS object ???
            vm.BFS = new BrowserFS.EmscriptenFS()  // {FS:vm.FS}
            vm.BFS.Buffer = BrowserFS.BFSRequire('buffer').Buffer
        }

        const track_media = MM[trackid].media

        if (!bfs2) {
            console.warn(" ==================== BFS1 ===============")
            BrowserFS.InMemory = BrowserFS.FileSystem.InMemory
            BrowserFS.OverlayFS = BrowserFS.FileSystem.OverlayFS
            BrowserFS.MountableFileSystem = BrowserFS.FileSystem.MountableFileSystem
            BrowserFS.ZipFS = BrowserFS.FileSystem.ZipFS

            function apk_cb(e, apkfs){
                console.log(__FILE__, "930 mounting", hint, "onto", track.mount.point)

                BrowserFS.InMemory.Create(
                    function(e, memfs) {
                        BrowserFS.OverlayFS.Create({"writable" :  memfs, "readable" : apkfs },
                            function(e, ovfs) {
                                BrowserFS.MountableFileSystem.Create({
                                    '/' : ovfs
                                    }, async function(e, mfs) {
                                        await BrowserFS.initialize(mfs)
                                        await vm.FS.mount(vm.BFS, {root: track.mount.path}, track.mount.point)                                    
                                        setTimeout(()=>{track.ready=true}, 0)
                                    })
                            }
                        );
                    }
                );
            }

            await BrowserFS.ZipFS.Create(
                {"zipData" : track_media, "name": hint},
                apk_cb
            )

        } else { // bfs1
            console.warn(" ==================== BFS2 ===============")

            // assuming FS is from Emscripten
            await BrowserFS.configure({
                fs: 'MountableFileSystem',
                options: {
                    '/': {
                        fs: 'OverlayFS',
                        options: {
                            readable: { fs: 'ZipFS', options: { zipData: track_media, name: 'hint'  } },
                            writable: { fs: 'InMemory' }
                        }
                    }
                }
            });

            vm.FS.mount(vm.BFS, { root: track.mount.path, }, track.mount.point);
            setTimeout(()=>{track.ready=true}, 0)
        } // bfs2



    } // track type mount
}


function MM_play(track, loops) {
    const media = track.media
    track.loops = loops
    const prom = track.media.play()
    if (prom){
        prom.then(() => {
            // ME ok play started
            MM.UME = true
        }).catch(error => {
            // Media engagement required
            MM.UME = false
            console.error(`** MEDIA USER ACTION REQUIRED [${track.test}] **`)
            if (track.test && track.test>0) {
                track.test += 1
                setTimeout(MM_play, 1000, track, loops)
            }

        });
    }
}




window.cross_track = async function cross_track(trackid, url, flags) {
    var response = await fetch(url, flags || FETCH_FLAGS);

    checkStatus(response)

    const reader = response.body.getReader();

    const len = Number(response.headers.get("Content-Length"));
    const track = MM[trackid]

    // concatenate chunks into single Uint8Array
    track.data = new Uint8Array(len);
    track.pos = 0
    track.len = len

    console.warn(url, track.len)

    while(true) {
        const {done, value} = await reader.read()

        if (done) {
            track.avail = true
            break
        }
        try {
            track.data.set(value, track.pos)
        } catch (x) {
            track.pos = -1
            console.error("1396: cannot download", url)
        }
        track.pos += value.length
    }

    console.log(`${trackid}:${url} Received ${track.pos} of ${track.len} to ${track.path}`)
    if (track.type === "fs" ) {
        FS.writeFile(track.path, track.data)
    }

}


MM.prepare = function prepare(url, cfg) {
    MM.tracks++;
    const trackid = MM.tracks
    var audio

    cfg = JSON.parse(cfg)


    const transport = cfg.io || 'packed'
    const type = cfg.type || 'fs'

    MM[trackid] = { ...cfg, ...{
            "trackid": trackid,
            "type"  : type,
            "url"   : url,
            "error" : false,
            "len"   : 0,
            "pos"   : 0,
            "io"    : transport,
            "ready" : undefined,
            "auto"  : false,
            "avail" : undefined,
            "media" : undefined,
            "data"  : undefined
        }
    }
    const track = MM[trackid]

//console.log("MM.prepare", trackid, transport, type)

    if (transport === 'fs') {
        if ( type === "audio" ) {
            const blob = new Blob([FS.readFile(track.url)])
            audio = new Audio(URL.createObjectURL(blob,  { oneTimeOnly: true }))
            track.avail = true
        } else {
            console.error("fs transport is only for audio", JSON.stringify(track))
            track.error = true
            return track
        }
    }

    if (transport === "url" ) {
        // audio tag can download itself
        if ( type === "audio" ) {
            audio = new Audio(url)
            track.avail = true
        } else {
console.log("MM.cross_track", trackid, transport, type, url )
            cross_track(trackid, url, {} )
        }
    }


    if (audio) {
        track.media = audio

        track.set_volume = (v) => { track.media.volume = 0.0 + v }
        track.get_volume = () => { return track.media.volume }
        track.stop = () => { track.media.pause() }

        track.play = (loops) => { MM_play( track, loops) }

        MM_autoevents(track, trackid)

    }

//console.log("MM.prepare", url,"queuing as",trackid)
    media_prepare(trackid)
//console.log("MM.prepare", url,"queued as",trackid)
    return track
}


MM.load = function load(trackid, loops) {
// loops =0 play once, loops>0 play number of time, <0 loops forever
    const track = MM[trackid]

    loops = loops || 0 //??=
    track.loops = loops

    if (!track.avail) {
        // FS not ready
        console.error("981 TODO: bounce with setTimeout")
        return 0
    }


    if (track.type === "audio") {
        MM_autoevents( track , trackid )
        return trackid
    }

    if (track.type === "mount") {
        const mount = track
        console.log(track.mount.point , track.mount.path, trackid )
        mount_ab( track.data , track.mount.point , track.mount.path, trackid )
        return trackid
    }
// unsupported type
    return -1
}


MM.play = function play(trackid, loops, start, fade_ms) {
    console.log("MM.play",trackid, loops, MM[trackid] )
    const track = MM[trackid]

    track.loops = loops

    if (track.ready) {
        track.media.play()
    } else {
        console.warn("Cannot play before user interaction, will retry", track )
        function play_asap() {
            if (track.ready) {
                track.media.play()
            } else {
                setTimeout(play_asap, 500)
            }
        }
        play_asap()
    }
}

MM.stop = function stop(trackid) {
    console.log("MM.stop", trackid, MM[trackid] )
    MM[trackid].media.currentTime = 0
    MM[trackid].media.pause()
    MM.current_trackid = 0
}

MM.get_pos = function get_pos(trackid) {
    if (MM.transition)
        return 0

    const track = MM[trackid]

    if (track && track.media)
        return MM[trackid].media.currentTime
    return -1
}



MM.pause = function pause(trackid) {
    console.log("MM.pause", trackid, MM[trackid] )
    MM[trackid].media.pause()
}

MM.unpause = function unpause(trackid) {
    console.log("MM.unpause", trackid, MM[trackid] )
    MM.current_trackid = trackid
    MM[trackid].media.play()
}

MM.set_volume = function set_volume(trackid, vol) {
    MM[trackid].media.volume = 1 * vol
}

MM.set_volume = function get_volume(trackid, vol) {
    return MM[trackid].media.volume
}

MM.set_socket = function set_socket(mode) {
    vm["websocket"]["url"] = mode
    console.log("WebSocket default mode is now :", mode)
}


function MM_autoevents(track, trackid) {
    const media = track.media

    if (media.MM_autoevents) {
        return
    }

    media.MM_autoevents = 1

    track.media.onplaying = (event) => {
        MM.transition = 0
        MM.current_trackid = trackid
    }

    media.addEventListener("canplaythrough", (event) => {
        track.ready = true
        if (track.auto) {
            media.play()
        }
    })

    media.addEventListener('ended', (event) => {

        if (track.loops<0) {
            console.log("track ended - looping forever")
            media.play()
            return
        }
        if (track.loops>0) {
            track.loops--;
            console.log("track ended - pass", track.loops)
            media.play()
            return
        }

        console.log("track ended - q?", MM.next_tid)

        // check a track is queued
        if (MM.next_tid) {
            MM.transition = 1
            console.log("queued", MM.next_hint, "from", MM.next, "loops", MM.next_loops)
            track.auto = true
            MM.play(MM.next_tid, MM.next_loops)
            MM.next_tid = 0
        }
    })
}


// js.MM.CAMERA

// TODO: https://ffmpegwasm.netlify.app/ https://github.com/ffmpegwasm
// TODO: write png in a wasm pre allocated array
// TODO: frame rate

window.MM.camera.started = 0
window.MM.camera.init = function * (device, width,height, preview, grabber) {
    if (!MM.camera.started) {
        var done = 0
        var rc = null
        const vidcap = document.createElement('video')
        vidcap.id = "vidcap"
        vidcap.autoplay = true

        window.vidcap = vidcap
        width = width || 640
        height = height || 480

        vidcap.width = width
        vidcap.height = height
        const device = MM.camera.device || "/dev/video0"



        MM.camera.fd = {}
        MM.camera.busy = 0

        // 60 fps
        MM.camera.frame = { device : undefined , rate : Number.parseInt(1000/30/4) }

        var framegrabber = null

        if (window.stdout) {

            if (preview)
                stdout.appendChild(vidcap)

            if (grabber) {
                framegrabber = document.createElement('canvas')
                stdout.appendChild(framegrabber)
            } else {

            }
        }

        if (!framegrabber)
            framegrabber = new OffscreenCanvas(width, height)
        else {
            framegrabber.width = width
            framegrabber.height = height
        }

        window.framegrabber = framegrabber

        function onCameraFail(e) {
            console.log('924: Camera did not start.', e)
            MM.camera.started = 0
            done =1
        }

        const params = {
            audio: false,
            video: {
                "width": { ideal: width },
                "height": {  ideal: height },
            }
        }


        MM.camera.query_image = function () {
            // ok to use previous image
            if ( FS.analyzePath(device).exists )
                return true
            if (MM.camera.busy>25)
                console.error("frame grabber is stuck")
            return false
        }

        // TODO: same but async
        MM.camera.get_raw = function * () {
            // capture next frame and wait conversion
            setTimeout(GRABBER, 0)
            while (!MM.camera.frame[device])
                yield 0
            return MM.camera.frame[device]
        }

        const reader = new FileReader()

        reader.addEventListener("load", () => {
                const data = new Int8Array(reader.result)
                FS.writeFile(device,  data )
                //console.log("frame ready at ", MM.camera.busy)
                MM.camera.frame[device] = data.length
                MM.camera.busy--
            }, false
        )

        async function GRABBER() {
            if (MM.camera.busy<25)
                setTimeout(GRABBER, MM.camera.frame["rate"])

            if (MM.camera.busy>0)
                return

            MM.camera.busy++
            framegrabber.getContext("2d").drawImage(vidcap, 0, 0);

            // convert the new frame !
            MM.camera.frame[device] = undefined
            MM.camera.blob = await framegrabber.convertToBlob({type:"image/png"})
            reader.readAsArrayBuffer(MM.camera.blob)
        }

        window.GRABBER = GRABBER

        function connection(stream) {
            vidcap.srcObject = stream
            vidcap.onloadedmetadata = function(e) {
                setTimeout(GRABBER, 0)
                console.log("video stream ready")
                MM.camera.started = 1
                done =1
            }
        }

        navigator.mediaDevices.getUserMedia(params) //, connection, onCameraFail)
        .then( stream => connection(stream) )
        .catch(e => onCameraFail(e))

        while (!done)
            yield 0

        // wait for first frame
        while (!MM.camera.frame[device])
            yield 0
    }
    yield window.MM.camera.started
}

//=========================================================
// js.SVG

window.svg = { }

window.svg.init = function () {
    if (svg.screen)
        return
    svg.screen = new OffscreenCanvas(canvas.width, canvas.height)
    svg.ctx = svg.screen.getContext('2d')

}

window.svg.render =  function * (path, dest) {
    var converted = 0
    svg.init()
    dest = dest || path + ".png"
    let blob = new Blob([FS.readFile(path)], {type: 'image/svg+xml'});
    let url = URL.createObjectURL(blob);

    svg.ctx.clearRect(0, 0, -1, -1);

    let rd = new Image();
        rd.src = url

    async function load_cleanup () {
        svg.ctx.drawImage(rd, 0, 0 )

        window.svg.blob = await svg.screen.convertToBlob()
        const reader = new FileReader()
        reader.addEventListener("load", () => {
            FS.writeFile(dest,  new Int8Array(reader.result) )
            console.log("svg conversion of", path,"to png complete :" , dest)
            converted = 1
          }, false
        );
        reader.readAsArrayBuffer(svg.blob)
        URL.revokeObjectURL(url)

    }
    rd.addEventListener('load', load_cleanup );
    while (!converted)
        yield converted
}

window.svg.draw = function (path, x, y) {
    svg.init()
    let blob = new Blob([FS.readFile(path)], {type: 'image/svg+xml'});
    let url = URL.createObjectURL(blob);

    const rd = new Image();
    rd.src = url
    function load_cleanup () {
        canvas.getContext('2d').drawImage(rd,x || 0, y || 0 )
        URL.revokeObjectURL(url)
    }
    rd.addEventListener('load', load_cleanup );
}

//=========================================================
// js.misc

window.chromakey = function(context, r,g,b, tolerance, alpha) {
    context = canvas.getContext('2d', { willReadFrequently: true } );

    var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    var data = imageData.data;

    r = r || data[0]
    g = g || data[1]
    b = b || data[2]
    tolerance = tolerance || 255;
    tolerance -= 255
    alpha = alpha || 0

    for(var i = 0, n = data.length; i < n; i += 4) {
        var diff = Math.abs(data[i] - r) + Math.abs(data[i+1] - g) + Math.abs(data[i+2] - b);
        if(diff <= tolerance) {
            data[i + 3] = alpha;
        }
    }
    context.putImageData(imageData, 0, 0);
}



window.mobile_check = function() {
    let check = false;
    (   function(a){
        if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))
            check = true;
        }
    )(navigator.userAgent||navigator.vendor||window.opera);
    return check;
}

window.mobile_tablet = function() {
    let check = false;
    (   function(a){
        if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))
            check = true;
        }
    )(navigator.userAgent||navigator.vendor||window.opera);
    return check;
}

window.mobile = () => {
    try {
        return navigator.userAgentData.mobile
    } catch (x) {
        console.warn("FIXME:", x)
    }

    return mobile_check()
}


if (navigator.connection) {
    if ( navigator.connection.type === 'cellular' ) {
        console.warn("Connection:","Cellular")
        if ( navigator.connection.downlinkMax <= 0.115) {
            console.warn("Connection:","2G")
        }
    } else {
        console.warn("Connection:","Wired")
    }
}


// js.FTDI

window.io = {}

async function open_port() {
    var device = new WebUSBSerialDevice();
console.log("device", device)
    var ports = await device.getAvailablePorts()
console.log("ports", ports);
    var port = await device.requestNewPort();
    const codec = new TextDecoder
    const coder = new TextEncoder()

    function cb(msg) {
        const data = codec.decode(msg)
        console.log("recv",data )
        window.io.port.data = port.data + data
    }

    port.read = () => {
        const data = window.io.port.data
        window.io.port.data = ""
        return data
    }

    port.write = (data) => {
        port.send(coder.encode(data))
    }

    var data = await port.connect(cb, (error)=>console.error(error) )
    window.io.port = port
}

window.io.open_serial = function * () {
    open_port()
    while (!window.io.port)
        yield 0
    yield window.io.port
}


//TODO: battery
    // https://developer.mozilla.org/en-US/docs/Web/API/BatteryManager/levelchange_event

//TODO: camera+audio cap
    //https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia

// https://developer.mozilla.org/en-US/docs/Web/API/Accelerometer

// https://developer.mozilla.org/en-US/docs/Web/API/AmbientLightSensor



window.debug = function () {
    vm.config.debug = true
    const debug_hidden =  false
    try {
        window.custom_onload(debug_hidden)

    } catch (x) {
        console.error("using debug UI default, because no custom_onload or failure")
        for (const e of ["pyconsole","system","iframe","transfer","info","box","terminal"] ) {
            if (window[e])
                window[e].hidden = debug_hidden
        }
    }
    vm.PyRun_SimpleString(`#!
shell.uptime()
`)
    window_resize()
}


window.blob = function blob(filename) {
    console.warn(__FILE__, "1458: TODO: revoke blob url")
    return URL.createObjectURL( new Blob([FS.readFile(filename)],  { oneTimeOnly: true }))
}

// ========================================
// js.RPC


window.rpc = { path : [], call : "", argv : [] }

function bridge(host) {
    const pybr = new Proxy(function () {}, {
    get(_, k, receiver) {
        rpc.path.push(k)
        return pybr
    },
    apply(_, o, argv) {
        const call = rpc.path.join(".")
        if (host === window.python) {
// TODO: rpc id / event serialisation
            queue_event("rpc", { "call": call, "argv" : argv, "rpcid": window.event} )
        } else {
            window.rpc.call = call
            window.rpc.argv = Array.from(argv)
            if (!argv.length) {
                console.error("event should always be first param")
                window.rpc.argv.unshift(window.event)
            } else if (argv.length>0 && (window.event!==argv[0])) {
                console.error("event should always be first param")
                window.rpc.argv.unshift(window.event)
            }
            host.click()
        }
        rpc.path.length=0
    }
  });
  return pybr
}


// ========================================
// js.FETCH


window.Fetch = {}

// generator functions for async fetch API
// script is meant to be run at runtime in an emscripten environment

// Fetch API allows data to be posted along with a POST request
window.Fetch.POST = function * POST (url, data, flags)
{
    // post info about the request
    console.log("POST: " + url + "\nData: " + data);
    var request = new Request(url, {method: 'POST', body: JSON.stringify(data)})
    var content = 'undefined';
    fetch(request, flags || {})
   .then(resp => resp.text())
   .then((resp) => {
        console.log(resp);
        content = resp;
   })
   .catch(err => {
         // handle errors
         console.log("An Error Occurred:")
         console.log(err);
    });

    while(content == 'undefined'){
        yield content;
    }
}

// Only URL to be passed
// when called from python code, use urllib.parse.urlencode to get the query string
window.Fetch.GET = function * GET (url, flags)
{
    console.log("GET: " + url);
    var request = new Request(url, { method: 'GET' })
    var content = 'undefined';
    fetch(request, flags || {})
   .then(resp => resp.text())
   .then((resp) => {
        console.log(resp);
        content = resp;
   })
   .catch(err => {
         // handle errors
         console.log("An Error Occurred:");
         console.log(err);
    });

    while(content == 'undefined'){
        // generator
        yield content;
    }
}



// ====================================================================================
//          pyodide compat layer
// ====================================================================================


window.loadPyodide =
    async function loadPyodide(cfg) {
        vm.runPython =
            function runPython(code) {
                console.warn("runPython N/I", code)
                vm.PyRun_SimpleString(code)
                return 'N/A'
            }

        console.warn("loadPyodide N/I")
        auto_start(cfg)
        auto_start = null
        await onload()
        onload = null
        await _until(defined)("python")
        vm.vt.xterm.write = cfg.stdout
        console.warn("using ", python)
        return vm
    }

// ====================================================================================
//          STARTUP
// ====================================================================================

async function onload() {
    var debug_hidden = true;

    // this is how emscripten "os layer" will find it
    window.Module = vm
    var debug_mobile_request
    try {
        debug_mobile_request = (window.top.location.hash.search("#debug-mobile")>=0)
    } catch (x) {
        console.warn("FIXME:", x )
        debug_mobile_request = false
    }

    const nuadm = mobile() || debug_mobile_request

    var debug_user
    try {
        // not always accessible on cross-origin object
        debug_user = window.top.location.hash.search("#debug")>=0
    } catch (x) {
        console.warn("FIXME:", x )
        debug_user = false
    }

    const debug_dev = vm.PyConfig.orig_argv.includes("-X dev") || vm.PyConfig.orig_argv.includes("-i")
    const debug_mobile = nuadm && ( debug_user || debug_dev )
    if ( debug_user || debug_dev || debug_mobile ) {
        debug_hidden = false;
        vm.config.debug = true
        if ( is_iframe() ){
            vm.config.gui_divider = 3
        } else {
            vm.config.gui_divider = vm.config.gui_divider || 2 //??=
        }
    }
    console.warn(`


== FLAGS : is_mobile(${nuadm}) dev=${debug_dev} debug_user=${debug_user} debug_mobile=${debug_mobile} ==



`)
    if ( is_iframe() ) {
        console.warn("======= IFRAME =========")
    }

    feat_lifecycle()

    // container for html output
    var html = document.getElementById('html')
    if (!html){
        html = document.createElement('div')
        html.id = "html"
        document.body.appendChild(html)
    }

    var has_vt = false

    for (const feature of vm.config.features) {
        if (feature.startsWith("3d")) {
            vm.config.user_canvas_managed = 3
        }

        if (feature.startsWith("embed")) {

            vm.config.user_canvas_managed = vm.config.user_canvas_managed || 1

            const canvasXd = feat_gui(true)
            if ( canvasXd.innerHTML.length > 20 ) {
                vm.PyConfig.frozen = "/tmp/to_embed.py"
            }
            // only canvas when embedding 2D/3D, stdxxx go to console.
            break
        }

        if (feature.startsWith("snd")) {
            feat_snd(debug_hidden)
        }

        if (feature.startsWith("gui")) {
            feat_gui(debug_hidden)
        }

        // file upload widget

        if (feature.startsWith("fs")) {
            await feat_fs(debug_hidden)
        }


        // TERMINAL

        if (!nuadm || debug_mobile) {
            if (feature.startsWith("vt")) {

                // simpleterm.js

                if (feature === "vt") {
                    await feat_vt(debug_hidden)
                }

                // xterm.js

                if (feature === "vtx") {
                    await feat_vtx(debug_hidden)
                }
                has_vt = true

            }
            if (feature.startsWith("stdout")){
                feat_stdout()
                has_vt = true
                config.quiet = true
            }

        } else {
            console.warn("NO VT/stdout on mobile, use remote debugger or explicit flag")
        }
    }

    // FIXME: forced minimal output until until remote debugger is a thing.
    if ( debug_mobile && !has_vt) {
        console.warn("764: debug forced stdout")
        feat_stdout()
        has_vt = true
    }

    if (window.custom_onload)
        window.custom_onload(debug_hidden)


    window.busy--;
    if (!config.quiet)
        vm.vt.xterm.write('OK\r\nPlease \x1B[1;3;31mwait\x1B[0m ...\r\n')



    if (window.window_resize)
        window_resize(vm.config.gui_divider)

// console.log("cleanup while loading wasm", "has_parent?", is_iframe(), "Parent:", window.parent)

    feat_snd = feat_gui = feat_fs = feat_vt = feat_vtx = feat_stdout = feat_lifecycle = onload = null

    if ( is_iframe() ) {
        try {
            if (window.top.blanker)
                window.top.blanker.style.visibility = "hidden"
        } catch (x) {
            console.error("FIXME:", x)
        }
    }


    if (!window.transfer) {
// <!--
        document.getElementById('html').insertAdjacentHTML('beforeend', `
<style>
    div.emscripten { text-align: center; }
</style>
<div id="transfer" align=center style="z-index: 5;">
    <div class="emscripten" id="status">Downloading...</div>
    <div class="emscripten">
        <progress value="0" max="200" id="progress"></progress>
    </div>
</div>
`);
// -->
    }

    console.warn("Loading python interpreter from", config.executable)
    jsimport(config.executable)

}

function auto_conf(cfg) {
    var url = cfg.url

    console.log("AUTOSTART", url, document.location.href, cfg.stdout)
    if (document.currentScript) {
        if (document.currentScript.async) {
            console.log("Executing asynchronously", document.currentScript.src);
        } else {
            console.log("Executing synchronously");
        }
    }


    const old_url = url

    var elems

    elems = url.rsplit('#',1)
    url = elems.shift()



    elems = url.rsplit('?',1)
    url = elems.shift()

console.warn("TODO: merge/replace location options over script options")

    if (url.endsWith(module_name)) {
        url = url + (window.location.search || "?") + ( window.location.hash || "#" )
        console.log("Location of",module_name,"overrides script", old_url ,'=>', url )
    }

    elems = url.rsplit('#',1)
    url = elems.shift()

    if (elems.length)
        for (const arg of elems.pop().split("%20") ) {
           vm.sys_argv.push(decodeURI(arg))
        }

    elems = url.rsplit('?',1)
    url = elems.shift()

    if (elems.length)
        for (const arg of elems.pop().split("&")) {
            vm.cpy_argv.push(decodeURI(arg))
        }


    var code = ""

    if (!cfg.module && cfg.text.length) {
        code = cfg.text
    } else {
        console.warn("1601: no inlined code found")
    }

    // resolve python executable, cmdline first then script
    var pystr = "cpython"

    if (vm.cpy_argv.length && (vm.cpy_argv[0].search('py')>=0)) {
        pystr = vm.cpy_argv[0]
    } else {
        if (cfg.python && (cfg.python.search('py')>=0)) {
            pystr = cfg.python
        }
        // fallback to cpython
    }

    if (pystr.search('cpython3')>=0) {
        vm.script.interpreter = "cpython"
        config.PYBUILD = pystr.substr(7) || "3.11"
    } else {
        if (pystr.search('python3')>=0) {
            vm.script.interpreter = "python"
            config.PYBUILD = pystr.substr(6) || "3.4"
        } else {
            if (pystr.search('wapy')>=0) {
                vm.script.interpreter = "wapy"
                config.PYBUILD = pystr.substr(4) || "3.4"
            } else {
                vm.script.interpreter = config.python || "cpython"
                config.PYBUILD = pystr.substr(7) || "3.11"
            }
        }
    }


    // running pygbag proxy, lan testing or a module url ?
    if ( (location.hostname === "localhost") || cfg.module) {
        config.cdn = url.split("?",1)[0].replace(module_name, "")
    }

    config.cdn     = config.cdn || url.split(module_name, 1)[0]  //??=
    config.pydigits =  config.pydigits || config.PYBUILD.replace(".","") //??=
    config.executable = config.executable || `${config.cdn}python${config.pydigits}/main.js` //??=


    // resolve arguments

    config.xtermjs = config.xtermjs || 0

    config.archive = config.archive || (location.search.search(".apk")>=0)  //??=

    config.debug = config.debug || (location.hash.search("#debug")>=0) //??=

//FIXME: should debug force -i or just display vt ?
config.interactive = config.interactive || (location.search.search("-i")>=0) //??=

    config.cols = cfg.cols || 132
    config.lines = cfg.lines || 32

    config.gui_debug = config.gui_debug ||  2  //??=

    if (config.id == "__main__")
        config.autorun = 1

    config.quiet = false
    config.can_close = config.can_close || 0
    config.autorun  = config.autorun || 0 //??=
    config.features = config.features || cfg.os.split(",") //??=

    config._sdl2    = config._sdl2 || "canvas" //??=

    if (config.ume_block === undefined) {
        config.ume_block = 1 //??=
    }

    console.log(JSON.stringify(config))


    // https://docs.python.org/3/c-api/init_config.html#initialization-with-pyconfig

    // TODO: https://docs.python.org/3/c-api/init_config.html#c.PyConfig.run_module
    // TODO: https://docs.python.org/3/c-api/init_config.html#c.PyConfig.bytes_warning
    // TODO: https://docs.python.org/3/c-api/init_config.html#c.PyConfig.program_name ( PYTHONEXECUTABLE )

    vm.PyConfig = JSON.parse(`
        {
            "isolated" : 0,
            "parse_argv" : 0,
            "quiet" : 0,
            "run_filename" : "main.py",
            "write_bytecode" : 0,
            "skip_source_first_line" : 1,
            "bytes_warning" : 1,
            "base_executable" : null,
            "base_prefix" : null,
            "buffered_stdio" : null,
            "bytes_warning" : 0,
            "warn_default_encoding" : 0,
            "code_debug_ranges" : 1,
            "check_hash_pycs_mode" : "default",
            "configure_c_stdio" : 1,
            "dev_mode" : -1,
            "dump_refs" : 0,
            "exec_prefix" : null,
            "executable" : "${config.executable}",
            "faulthandler" : 0,
            "filesystem_encoding" : "utf-8",
            "filesystem_errors" : "surrogatepass",
            "use_hash_seed" : 1,
            "hash_seed" : 1,
            "home": null,
            "import_time" : 0,
            "inspect" : 1,
            "install_signal_handlers" :0 ,
            "interactive" : ${config.interactive},
            "legacy_windows_stdio":0,
            "malloc_stats" : 0 ,
            "platlibdir" : "lib",
            "prefix" : "/data/data/org.python/assets/site-packages",
            "ps1" : ">>> ",
            "ps2" : "... "
        }`)

    vm.PyConfig.argv = vm.sys_argv
    vm.PyConfig.orig_argv = vm.cpy_argv

    for (const prop in config)
        console.log(`config.${prop} =`, config[prop] )

    console.log('interpreter=', vm.script.interpreter)
    console.log('orig_argv', vm.PyConfig.orig_argv)
    console.log('sys.argv: ' , vm.PyConfig.argv)
    console.log('docurl=', document.location.href)
    console.log('srcurl=', url)
    if (!cfg.module) {
        console.log('data-os=', config.os)
        console.log('data-python=', config.python)
        console.log('script: id=', config.id)
        console.log('code : ' , code.length, ` as ${config.id}.py`)
    }
    vm.config = config
}


function auto_start(cfg) {
    window.busy = 1
    if (cfg) {
        console.error("not using python script tags")
        cfg.os = "gui"
        //config.id = "__main__"
        cfg.module = true
        auto_conf(cfg)
        vm.script.blocks = [ "print(' - Pygbag runtime -')" ]
    } else {
        for (const script of document.getElementsByTagName('script')) {
            if ( (script.type == 'module') && (script.src.search(module_name) >= 0)){
                const code = script.text
                cfg = {
                    module : false,
                    python : script.dataset.python,
                    cols : script.dataset.cols,
                    lines : script.dataset.lines,
                    url : script.src,
                    os : script.dataset.os || "gui",
                    text : code,
                    id : script.id,
                    autorun : ""
                }

                window.addEventListener("load", onload )
                auto_conf(cfg)

                if (vm.config.autorun)
                    code = code + `
    if sys.platform in ('emscripten','wasi'):
        embed.run()
`

                vm.script.blocks = [ code ]

                // only one script tag for now
                break
            } else {
                console.log("script?", script.type, script.id, script.src, script.text )
            }
        }

        for (const script of document.getElementsByTagName('script')) {
            //TODO: process py-script brython whatever and push to vm.script.blocks
            // for concat with vm.FS.writeFile
        }

    }

}


window.set_raw_mode = function (param) {
    window.RAW_MODE = param || 0
}



auto_start()
