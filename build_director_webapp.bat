cd aurelia-webapp

au build

cd ..

xcopy aurelia-webapp\index.html static\index.html

xcopy /E aurelia-webapp\src static\
