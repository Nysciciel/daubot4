set cwd=%cd%
set DofusInvoker=\Local\Ankama\zaap\dofus\DofusInvoker.swf
set selectclass=com.ankamagames.dofus.BuildInfos,com.ankamagames.dofus.network.++,com.ankamagames.jerakine.network.++
set ffdecFolder=C:\Program Files (x86)\FFDec
set dst=%cd%
cd %ffdecFolder%
java -jar ffdec.jar -selectclass %selectclass% -export script %dst%/sources %Appdata%\..%DofusInvoker%
cd %cwd%
py build_protocol.py
pause