# Confirmatory environment freeze

Machine-specific execution environment; abort on version or NumPy build drift.

OS: macOS-15.6.1-arm64-arm-64bit
Python: 3.12.5

```json
{
  "python": "3.12.5",
  "system": "Darwin",
  "release": "24.6.0",
  "machine": "arm64",
  "packages": {
    "numpy": "2.4.4",
    "scipy": "1.17.1",
    "cvxpy": "1.8.2",
    "scs": "3.2.11",
    "pandas": "3.0.2"
  },
  "numpy_build": {
    "Compilers": {
      "c": {
        "name": "clang",
        "linker": "ld64",
        "version": "15.0.0",
        "commands": "cc"
      },
      "cython": {
        "name": "cython",
        "linker": "cython",
        "version": "3.2.4",
        "commands": "cython"
      },
      "c++": {
        "name": "clang",
        "linker": "ld64",
        "version": "15.0.0",
        "commands": "c++"
      }
    },
    "Machine Information": {
      "host": {
        "cpu": "aarch64",
        "family": "aarch64",
        "endian": "little",
        "system": "darwin"
      },
      "build": {
        "cpu": "aarch64",
        "family": "aarch64",
        "endian": "little",
        "system": "darwin"
      }
    },
    "Build Dependencies": {
      "blas": {
        "name": "accelerate",
        "found": true,
        "version": "unknown",
        "detection method": "system",
        "include directory": "unknown",
        "lib directory": "unknown",
        "openblas configuration": "unknown",
        "pc file directory": "unknown"
      },
      "lapack": {
        "name": "accelerate",
        "found": true,
        "version": "unknown",
        "detection method": "system",
        "include directory": "unknown",
        "lib directory": "unknown",
        "openblas configuration": "unknown",
        "pc file directory": "unknown"
      }
    },
    "Python Information": {
      "path": "/private/var/folders/bb/km69qtt53nlbxc29ljr4c9d00000gn/T/build-env-8jz__88i/bin/python",
      "version": "3.12"
    },
    "SIMD Extensions": {
      "baseline": [
        "NEON",
        "NEON_FP16",
        "NEON_VFPV4",
        "ASIMD"
      ],
      "found": [
        "ASIMDHP",
        "ASIMDDP"
      ],
      "not found": [
        "ASIMDFHM"
      ]
    }
  },
  "scipy_build": {
    "Compilers": {
      "c": {
        "name": "clang",
        "linker": "ld64",
        "version": "15.0.0",
        "commands": "cc"
      },
      "cython": {
        "name": "cython",
        "linker": "cython",
        "version": "3.2.4",
        "commands": "cython"
      },
      "c++": {
        "name": "clang",
        "linker": "ld64",
        "version": "15.0.0",
        "commands": "c++"
      },
      "fortran": {
        "name": "gcc",
        "linker": "ld64",
        "version": "13.4.0",
        "commands": "gfortran"
      },
      "pythran": {
        "version": "0.18.1",
        "include directory": "../../../../../../private/var/folders/7x/mtlmm33x08j4_89tfb27m_x00000gn/T/build-env-wl6q4faf/lib/python3.12/site-packages/pythran"
      }
    },
    "Machine Information": {
      "host": {
        "cpu": "aarch64",
        "family": "aarch64",
        "endian": "little",
        "system": "darwin"
      },
      "build": {
        "cpu": "aarch64",
        "family": "aarch64",
        "endian": "little",
        "system": "darwin"
      },
      "cross-compiled": false
    },
    "Build Dependencies": {
      "blas": {
        "name": "Accelerate",
        "found": true,
        "version": "unknown",
        "detection method": "extraframeworks",
        "include directory": "unknown",
        "lib directory": "unknown",
        "openblas configuration": "unknown",
        "pc file directory": "unknown",
        "has ilp64": false
      },
      "lapack": {
        "name": "Accelerate",
        "found": true,
        "version": "unknown",
        "detection method": "extraframeworks",
        "include directory": "unknown",
        "lib directory": "unknown",
        "openblas configuration": "unknown",
        "pc file directory": "unknown",
        "has ilp64": false
      },
      "pybind11": {
        "name": "pybind11",
        "version": "3.0.2",
        "detection method": "config-tool",
        "include directory": "unknown"
      }
    },
    "Python Information": {
      "path": "/private/var/folders/7x/mtlmm33x08j4_89tfb27m_x00000gn/T/build-env-wl6q4faf/bin/python",
      "version": "3.12"
    }
  },
  "thread_environment": {
    "OMP_NUM_THREADS": null,
    "OPENBLAS_NUM_THREADS": null,
    "MKL_NUM_THREADS": null,
    "VECLIB_MAXIMUM_THREADS": null
  }
}
```

Complete package lock: `CONFIRMATORY_REQUIREMENTS_LOCK.txt`.
Its SHA-256: 4a597ff76543496a7af7460a85ea67ea9f6cda7072e1fdeb8c4548b37e492239

Environment JSON SHA-256: ad65453dd255042d07b379c3ae396e973d487b17130e411f776da1256dd5f2eb
Execution interpreter: code/.venv/bin/python. NumPy BLAS/build configuration is recorded above.
