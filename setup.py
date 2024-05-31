# Copyright (c) Tiago Ribeiro

import os, sys, subprocess
from setuptools import find_packages, setup
from setuptools.command.install import install

DownloadPyOpenGLUnofficial = "https://drive.google.com/drive/folders/1mz7faVsrp0e6IKCQh8MyZh-BcCqEGPwx"
DownloadPyTorch = "https://pytorch.org/get-started/locally/"

def run_pip(*args):
    try:
        subprocess.run(["python", "-m", "pip", *args], text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' return with error (code {e.returncode}): {e.output}")

def checkGLUT():
    try:
        from OpenGL import GLUT
        return True
    except:
        return False
    
def checkPyTorchCUDA():
    try:
        import torch
        if torch.cuda.is_available():
            return True
        else:
            return False
    except:
        return False

def _post_install():
    print('POST INSTALL')
    
    print("PyTorch CUDA Check:", checkPyTorchCUDA())
    if not checkPyTorchCUDA():
        run_pip("install", "torch", "--index-url", "https://download.pytorch.org/whl/cu121")
        
    print("GLUT Check:", checkGLUT())
    if not checkGLUT():
        print("Please download PyOpenGL wheels from the following link and install them manually using 'pip3 install <file.whl>: ", DownloadPyOpenGLUnofficial)  


class CustomInstallCommand(install):
    def run(self):
        os.system("echo Installing NeuroNutty using custom install script...")
        install.run(self)
        _post_install()
        

setup(
    name="neuronutty",
    version="0.0.2",
    description="NeuroNutty is a toolkit based on Fairmotion to help train and evaluate neural networks for motion prediction and generation.",
    url="https://github.com/tiagrib/neuronutty",
    author="Tiago Ribeiro",
    author_email="me@tiagoribeiro.pt",
    cmdclass={'install': CustomInstallCommand},
    install_requires=[
        "black",
        "dataclasses",
        "matplotlib==3.9.0",
        "numpy",
        "pillow",
        "pyrender==0.1.39",
        "scikit-image",
        "scikit-learn",
        "scipy",
        "torch==2.3.0",
        "tqdm",
        "PySide6",
        "PyOpenGL==3.1.0",
        "PyOpenGL-accelerate",
        "body_visualizer @ git+https://github.com/nghorbani/body_visualizer.git@be9cf756f8d1daed870d4c7ad1aa5cc3478a546c",
        "human_body_prior @ git+https://github.com/nghorbani/human_body_prior.git@0278cb45180992e4d39ba1a11601f5ecc53ee148",
    ],
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
