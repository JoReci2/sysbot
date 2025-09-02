*** Settings ***
Name           linux.podman

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        22

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***
version method works
    ${output}=    Call Components    modules.linux.podman.version    target    runas=True
    Should Be Equal    ${output}[Client][Os]    linux

configuration method works
    ${output}=    Call Components    modules.linux.podman.configuration    target    runas=True
    Should Be Equal    ${output}[host][arch]    amd64

containers method works
    ${output}=    Call Components    modules.linux.podman.containers    target    runas=True
    Should Not Be Empty    ${output}

container_inspect method works
    ${output}=    Call Components    modules.linux.podman.container_inspect    target    test    runas=True
    Should Not Be Empty    ${output}

pods method works
    ${output}=    Call Components    modules.linux.podman.pods    target    runas=True
    Should Not Be Empty    ${output}

pod_inspect method works
    ${output}=    Call Components    modules.linux.podman.pod_inspect    target    test    runas=True
    Should Not Be Empty    ${output}

volumes method works
    ${output}=    Call Components    modules.linux.podman.volumes    target    runas=True
    Should Not Be Empty    ${output}

volume_inspect method works
    ${output}=    Call Components    modules.linux.podman.volume_inspect    target    test    runas=True
    Should Not Be Empty    ${output}

images method works
    ${output}=    Call Components    modules.linux.podman.images    target    runas=True
    Should Not Be Empty    ${output}

image_inspect method works
    ${output}=    Call Components    modules.linux.podman.image_inspect    target    quay.io/podman/hello:latest    runas=True
    Should Not Be Empty    ${output}
