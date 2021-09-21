set cwd=%cd%
set DofusFiles=%Appdata%\..\Local\Ankama\zaap\dofus
set json=%cwd%\..\misc\json
set input=%cwd%\..\misc\pydofus\input
set output=%cwd%\..\misc\pydofus\output
set dlm=%cwd%\..\misc\dlm
set pydofus=%cwd%\..\misc\pydofus

COPY %DofusFiles%\data\common\SubAreas.d2o %input%
COPY %DofusFiles%\data\common\MapPositions.d2o %input%
COPY %DofusFiles%\data\common\PointOfInterest.d2o %input%

cd %DofusFiles%\content\maps
for /r %%i in (*.d2p) do COPY /y %%i %input%

cd %pydofus%
py d2o_unpack.py
py d2p_unpack.py

cd %cwd%\..\misc\pydofus\
for /r %%i in (*.dlm) do COPY /y %%i ..\dlm

cd %cwd%
COPY %output%\SubAreas.json %json%
COPY %output%\MapPositions.json %json%
COPY %output%\PointOfInterest.json %json%

COPY %DofusFiles%\data\i18n\i18n_fr.d2i %json%
py ..\misc\pydofus\d2i_unpack.py %json%\i18n_fr.d2i