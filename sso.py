import glob

import jpype.imports


def get_jar_file_list(path: str):
    """
    path 위치의 모든 jar 파일 목록을 Return 하는 함수
    * path example)
      - /app/somjang/solution/jar_files
    :param path: jar 파일이 위치해 있는 디렉토리 경로
    :return: path 위치의 모든 jar 파일 목록
    """
    return glob.glob(path)

path = "ssoAgent/WEB-INF/lib/nets-nsso-agent-core.jar"
jar_file_list = get_jar_file_list(path=path)

jpkg = jpype.startJVM(classpath=jar_file_list)