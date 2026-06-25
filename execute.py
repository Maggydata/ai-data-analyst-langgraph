import os
import sys
import subprocess
import tempfile
from dataclasses import dataclass, field


@dataclass
class ExecutionResult :
    """Result of an execution"""
    """This is what the Coder reads to decide whether or not to correct itself"""
    success : bool                                          #For code execution
    stdout : str                                            #what the code printed
    stderr : str                                            #Error
    returncode : int                                        #0 = success, other = failed, -1 = timeout
    figure_files : list = field(default_factory = list)     #Producted figN.json files
    workdir :str = ""                                       #temporary folder used
    
    

def run_generated_code(code : str, csv_path : str, timeout : int = 30) -> ExecutionResult :
    """Runs 'code' in an isolated Python process."""
     
    #directory of temporary and isolated work 
    workdir = tempfile.mkdtemp(prefix = "coder_run_")
    script_path = os.path.join(workdir, "analysis.py")
    with open(script_path, "w", encoding="utf-8") as f :
         f.write(code)
    
    
    #A minimal environment, just PATH to locate the interpreter
    env = {"PATH" : os.environ.get("PATH", "")}
    
    #execution in separate process with TIMEOUT
    try:
        proc = subprocess.run(
            [sys.executable, script_path, os.path.abspath(csv_path)],
            cwd = workdir,              #Code work in temporary folder
            env = env,                  #environment
            capture_output = True,      #captures both stdout and stderr
            text = True,                
            timeout = timeout,          #infinite loop guard
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success = False, stdout = "", stderr = f"TIMEOUT: expired {timeout}s", 
            returncode = -1, figure_files = [], workdir=workdir  )
    
    #retrieval of the generated figures
    figures = sorted(
        os.path.join(workdir, fn)
        for fn in os.listdir(workdir)
        if fn.startswith("fig") and fn.endswith(".json")
    )
    
    return ExecutionResult(
        success = (proc.returncode == 0), 
        stdout = proc.stdout,
        stderr = proc.stderr, 
        returncode = proc.returncode,
        figure_files = figures,
        workdir = workdir
    ) 
    
 
#Test
if __name__ =="__main__" :
    from config import CSV_PATH
    
    #Scenario 1 : correct code
    good = (
        "import sys, pandas as pd, plotly.express as px\n"
        "df = pd.read_csv(sys.argv[1], encoding='latin-1')\n"
        "g = df.groupby('Region')['Sales'].sum().reset_index()\n"
        "fig = px.bar(g, x='Region', y='Sales')\n"
        "fig.write_json('fig0.json')\n"
        "print('lignes lues :', len(df))\n"
    )  
    
    #Scenario 2 : Break code
    broken = (
        "import sys, pandas as pd\n"
        "df = pd.read_csv(sys.argv[1], encoding='latin-1')\n"
        "print(df['ColonneQuiNexistePas'])\n"
    )
    
    #scenario 3 : infinite loop
    loop = "while True : \n      pass\n"
    
    for name, code in [("Correct", good), ("Break", broken), ("Loop", loop)] : 
        print (f"\n===== Scénario {name} =====")
        r = run_generated_code(code, CSV_PATH, timeout=5)
        print(f"success     : {r.success}")
        print(f"returncode   : {r.returncode}")
        print(f"figures   : {len(r.figure_files)}")
        if r.stdout :
            print(f"stdout      : {r.stdout.strip()}")
        if r.stderr:
            print(f"stderr      : {r.stderr.strip()[:200]}")    
    
    
    
