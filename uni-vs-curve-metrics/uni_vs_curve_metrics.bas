Attribute VB_Name = "Module1"
Sub SampleCall()
    mymodule = Left(ThisWorkbook.Name, (InStrRev(ThisWorkbook.Name, ".", -1, vbTextCompare) - 1))
    RunPython "import " & mymodule & ";" & mymodule & ".main()"
End Sub

Sub SampleRemoteCall()
    RunRemotePython "http://127.0.0.1:8000/hello", apiKey:="DEVELOPMENT"
End Sub
