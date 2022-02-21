git add .
set /p Var="commit -m: "
git commit -m %Var%
git push
pause