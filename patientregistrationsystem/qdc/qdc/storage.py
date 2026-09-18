from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class LegacyManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Manifest storage tolerante a assets faltantes.

    Fase5: libs vendored (Bootstrap 3 era, ex. BootstrapFormHelpers)
    referenciam arquivos que não existem no pacote (ex. dist/img/eu.png).
    O modo estrito abortaria o collectstatic; aqui arquivos existentes
    ganham hash normalmente e referências quebradas passam com warning.
    Não adicionar assets novos dependendo desse comportamento.
    """

    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        # Fase5: no 5.x o post-process levanta ValueError p/ refs inexistentes
        # independente de manifest_strict. Retorna URL original nesses casos.
        try:
            return super().hashed_name(name, content, filename)
        except ValueError:
            return name
