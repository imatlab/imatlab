if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp
    from ._kernel import MatlabKernel

    IPKernelApp.launch_instance(kernel_class=MatlabKernel)
