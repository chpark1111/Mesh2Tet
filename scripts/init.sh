echo "Building ManifoldPlus"
cd ../ManifoldPlus
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j8
echo "Finished building ManifoldPlus"
echo "Building fTetWild"
cd ../../fTetWild
mkdir build
cd build
cmake ..
make
echo "Finished building fTetwild"