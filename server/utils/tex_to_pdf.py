import subprocess
import os
from pathlib import Path
from typing import Optional

class TeXCompiler:
    def __init__(self, engine: str = "pdflatex"):
        self.engine = engine
        self.available_engines = ['pdflatex', 'xelatex', 'lualatex']
        
        if engine not in self.available_engines:
            raise ValueError(f"Unsupported engine: {engine}")
    
    def compile(
        self, 
        tex_file: str, 
        output_dir: Optional[str] = None,
        clean: bool = True,
        times: int = 1
    ) -> bool:
         
        tex_path = Path(tex_file)
        if not tex_path.exists():
            print(f"File not found: {tex_file}")
            return False
        
        # set output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = tex_path.parent
        
        # build command
        cmd = [
            self.engine,
            '-interaction=nonstopmode',
            f'-output-directory={output_path}',
            str(tex_path)
        ]
        
        try:
            print(f"Start compiling: {tex_file}")
            
            # multiple compilations
            for i in range(times):
                print(f"  {i+1}/{times} times compiling...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=tex_path.parent
                )
                
                if result.returncode != 0:
                    print(f"✗ compilation failed:\n{result.stdout[-500:]}")  
                    return False
            
            # clean temporary files
            if clean:
                self._clean_aux_files(tex_path, output_path)
            
            pdf_file = output_path / tex_path.with_suffix('.pdf').name
            print(f"Compilation successful: {pdf_file}")
            return True
            
        except subprocess.TimeoutExpired:
            print("Compilation timed out")
            return False
        except FileNotFoundError:
            print(f"Not found {self.engine}, please install TeX distribution")
            return False
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def _clean_aux_files(self, tex_path: Path, output_dir: Path):
        """clean auxiliary files"""
        aux_extensions = ['.aux', '.log', '.out', '.toc', '.bbl', '.blg']
        base_name = tex_path.stem
        
        for ext in aux_extensions:
            aux_file = output_dir / f"{base_name}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except Exception:
                    pass

# example
if __name__ == "__main__":
    compiler = TeXCompiler(engine="xelatex")  
    
    success = compiler.compile(
        tex_file="weekly_report.tex",
        output_dir="./reports",
        clean=True,
        times=2
    )
    
    if success:
        print("PDF generation completed!")