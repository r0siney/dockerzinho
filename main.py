import docker
import tarfile
import io
# import pywintypes

client = docker.from_env()

info = client.info()

print(f"SYSTEM: {info['OSType']}")

if info["OSType"] == "windows":
    image = "mcr.microsoft.com/windows/nanoserver:ltsc2019"
    cmd = """\
@echo off
ver
date /t
FOR /L %%G IN (1,1,2) DO (
    echo %%G
    ver
)
        """
    script = "script.bat"
    tarball_path = "C:\\"
    entrypoint = f"cmd.exe /k {tarball_path}{script}"
else:
    image = "ubuntu"
    cmd = """\
#!/bin/bash
for i in $(seq 1 10); do
    echo $i
    sleep 0.1
done
    """
    script = "script"
    tarball_path = "/"
    entrypoint = f"/bin/bash {tarball_path}{script}"


client.images.pull(repository=image)
container = client.containers.create(image=image, command=entrypoint)


source = io.BytesIO(initial_bytes=bytes(cmd, "utf-8"))

tarball = io.BytesIO()

with tarfile.open(fileobj=tarball, mode="w") as t:
    info = tarfile.TarInfo(script)
    info.size = len(cmd)
    t.addfile(info, source)

container.put_archive(tarball_path, tarball.getvalue())


output = container.attach(stdout=True, stderr=True, stream=True)

container.start()

print("output")

try:
    for line in output:
        print(line.decode("utf-8"), end="")
except Exception as err:
    pass # this exception only occurs in windows


result = container.wait()

print(f"result: {result}")

container.remove()