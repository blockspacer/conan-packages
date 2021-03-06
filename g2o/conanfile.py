from conans import ConanFile, CMake, tools
import os
import shutil

class G2OConan(ConanFile):
  name = "g2o"
  url = "http://www.intence.de"
  settings = "os", "compiler", "build_type", "arch"
  options = {"shared": [True, False]}
  default_options = "shared=True" 
  generators = "cmake"
  version = "2e35669"
  
  def requirements(self):
    self.requires("suitesparse/5164583@%s/%s" %( self.user, self.channel) )
     
    self.requires("Eigen3/3.3.4@%s/%s" %( self.user, self.channel))

  def source(self):
    #self.run('git clone --branch %s --single-branch https://github.com/RainerKuemmerle/g2o.git' % (self.version) )
    self.run('git clone https://github.com/RainerKuemmerle/g2o.git' )
    self.run('git checkout %s' % (self.version),cwd="g2o" )
    

  def build(self):
    
    tools.replace_in_file("g2o/CMakeLists.txt","""PROJECT(g2o)""","""PROJECT(g2o)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")

    #fix wrong define
    tools.replace_in_file("g2o/CMakeLists.txt","""ADD_DEFINITIONS(-DWINDOWS)""",
    """ADD_DEFINITIONS(-DWINDOWS)
       ADD_DEFINITIONS(-Od)
ADD_DEFINITIONS(-D_WINDOWS)""")


    #tools.replace_in_file("g2o/CMakeLists.txt","""FIND_PACKAGE(CSparse)""","""FIND_PACKAGE(CSparse NO_CMAKE_SYSTEM_PATH)""")

    #fix Non-C++11 compatibility
    #tools.replace_in_file("g2o/g2o/core/dynamic_aligned_buffer.hpp","""m_size{ 0 }, m_ptr{ nullptr }""","""m_size( 0 ), m_ptr( nullptr )""")
    
    #fix very strange compiler issue with VS2010 SP1
    tools.replace_in_file("g2o/g2o/core/sparse_optimizer.cpp",
    """estimatePropagator.propagate(fixedVertices, costFunction);""",
    """estimatePropagator.propagate(fixedVertices, costFunction, EstimatePropagator::PropagateAction(),numeric_limits<double>::max(),numeric_limits<double>::max());""")
    
    
    #fix cmake package detection
    if ( self.settings.compiler == "Visual Studio"):
        os.remove("g2o/cmake_modules/FindBLAS.cmake")
        os.remove("g2o/cmake_modules/FindLAPACK.cmake")
    
    os.remove("g2o/cmake_modules/FindCSparse.cmake")
    os.remove("g2o/cmake_modules/FindSuiteSparse.cmake")
    os.remove("g2o/cmake_modules/FindCholmod.cmake")
        

    cmake = CMake(self,parallel=True)

    if self.options.shared:
      cmake.definitions["BUILD_SHARED_LIBS"] = "ON" 
    
    cmake.definitions["CMAKE_INSTALL_PREFIX"] = "install"
    cmake.definitions["G2O_BUILD_EXAMPLES"] = "OFF"
    cmake.definitions["G2O_BUILD_APPS"] = "ON"
    cmake.definitions["G2O_USE_CSPARSE"] = "ON"
    cmake.definitions["BUILD_CSPARSE"] = "OFF"

    
    cmake.configure(source_dir="g2o",build_dir="." )
    cmake.build()
    cmake.install()


  def package(self):
    self.copy("*", src="install", dst=".")
    self.copy("FindG2O.cmake", src="g2o/cmake_modules", dst=".",keep_path=False)

  def package_info(self):
    libs = [
            "g2o_core", 
            "g2o_cli",
            "g2o_opengl_helper",
            "g2o_ext_freeglut_minimal",
            "g2o_solver_pcg", 
            "g2o_solver_eigen", 
            "g2o_solver_dense", 
            "g2o_solver_cholmod",
            "g2o_solver_csparse",
            "g2o_solver_structure_only",
            "g2o_solver_slam2d_linear",
            "g2o_stuff", 
            "g2o_types_data",
            "g2o_types_icp", 
            "g2o_types_sba",
            "g2o_types_sclam2d", 
            "g2o_types_sim3",
            "g2o_types_slam2d_addons", 
            "g2o_types_slam2d", 
            "g2o_types_slam3d_addons",
            "g2o_types_slam3d"
            ]


    if self.settings.build_type == 'Debug':
     self.cpp_info.libs = [ name+"_d" for name in libs ]
    else:
      self.cpp_info.libs = libs

    self.cpp_info.includedirs = ['include']  # Ordered list of include paths
    self.cpp_info.libdirs = ['lib']  # Directories where libraries can be found
    self.cpp_info.bindirs = ['bin']  # Directories where executables and shared libs can be found
