
from django.db import models
from django.contrib.auth.models import User
from django.http import request


class Base(models.Model):

    criado_em = models.DateTimeField('Criado em', auto_now_add=True, blank=False, null=False)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True


class Time(Base):

    nome = models.CharField('Nome', max_length=255, blank=False, null=False)
    local = models.CharField('Local', max_length=255, blank=False, null=False)

    def __str__(self):
        return self.nome


class Campeonato(Base):

    nome = models.CharField('Nome', max_length=255, blank=False, null=False)
    local = models.CharField('Local', max_length=255, blank=False, null=False)

    def __str__(self):
        return self.nome


class Bilhete(Base):

    valor = models.FloatField('Valor', blank=False, null=False)
    premio = models.FloatField('Premio', default=0.0, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bilhetes', blank=False, null=False)
    premiado = models.BooleanField('Premiado', max_length=255, default=False, blank=False, null=False)

    def total_apostas(self):
        return len(self.apostas.all())

    def atualiza_status(self):
        self.premiado = True
        for aposta in self.apostas.all():
            if not aposta.acertou:
                self.premiado = False
                break
        self.save()

    def cota_a_distribuir(self):
        cota = self.valor / self.total_apostas()
        return cota

    def __str__(self):
        return "Bilhete %d " % (self.id + 1000)


class Jogo(Base):

    STATUS_JOGO = (
        ('aberto', 'ABERTO'),
        ('em_espera', 'EM ESPERA'),
        ('fechado', 'FECHADO')
    )

    RESULTADO_JOGO = (
        ('empate', 'EMPATE'),
        ('casa', 'CASA'),
        ('fora', 'FORA')
    )

    time_casa = models.ForeignKey('Time', on_delete=models.CASCADE, related_name='jogos_mandante', blank=False, null=False)
    time_fora = models.ForeignKey('Time', on_delete=models.CASCADE, related_name='jogos_visitante', blank=False, null=False)
    local = models.CharField('Local', max_length=255, blank=False, null=False)
    data = models.DateTimeField('Data', blank=False, null=False)
    campeonato = models.ForeignKey('Campeonato', on_delete=models.CASCADE, related_name='partidas', blank=False, null=False)
    status = models.CharField('Status', max_length=64, default='aberto', choices=STATUS_JOGO, blank=False, null=False)
    resultado = models.CharField('Resultado', max_length=64, choices=RESULTADO_JOGO, blank=True, null=True)
    valor_total_apostado = models.FloatField('Valor total apostado', default=0.0, blank=True, null=True)
    rodada = models.ForeignKey('Rodada', on_delete=models.CASCADE, related_name='jogos', blank=False, null=False)

    def finalizar(self):
        if self.resultado != None and self.status != 'fechado':
            self.status = 'fechado'
            apostas = self.apostas_realizadas.all()
            for aposta in apostas:
                aposta.atualiza_status()
        self.save()

    def calcula_montante_jogo(self):
        if self.valor_total_apostado == 0.0:
            for aposta in self.apostas_realizadas.all():
                self.valor_total_apostado += round(aposta.bilhete.cota_a_distribuir(), 2)
                self.save()

    def distribuir_premio(self):
        bilhetes_premiados = []
        bilhetes = Bilhete.objects.filter(premiado=True)

        if len(bilhetes) > 0:
            for bilhete in bilhetes:
                for aposta in bilhete.apostas.all():
                    if aposta.jogo.id == self.id and not bilhetes_premiados.__contains__(bilhete):
                        bilhetes_premiados.append(bilhete)
                        break

            valor_a_distribuir = (0.8 * self.valor_total_apostado) / len(bilhetes_premiados)


            for bilhete in bilhetes_premiados:
                bilhete.premio += valor_a_distribuir
                bilhete.save()

    def __str__(self):
        return "%s x %s" %(self.time_casa, self.time_fora)

    def save(self):
        self.local = self.time_casa.local
        super(Jogo, self).save()


class Rodada(Base):

    nome = models.CharField('Nome', max_length=255, blank=False, null=False)

    def finalizar(self):
        for jogo in self.jogos.all():
            jogo.finalizar()
            jogo.calcula_montante_jogo()

        for jogo in self.jogos.all():
            jogo.distribuir_premio()

    def __str__(self):
        return self.nome


class Aposta(Base):

    TIPOS_APOSTA = (
        ('empate', 'EMPATE'),
        ('casa', 'CASA'),
        ('fora', 'FORA')
    )

    jogo = models.ForeignKey('Jogo', on_delete=models.CASCADE, related_name='apostas_realizadas', blank=False, null=False)
    tipo = models.CharField('Tipo', max_length=255, choices=TIPOS_APOSTA, blank=False, null=False)
    bilhete = models.ForeignKey('Bilhete', on_delete=models.CASCADE, related_name='apostas', blank=False, null=False)
    acertou = models.BooleanField('Acertou', max_length=255, default=False, blank=False, null=False)

    def atualiza_status(self):
        if self.tipo == self.jogo.resultado:
            self.acertou = True
            self.save()
            self.bilhete.atualiza_status()

    def __str__(self):
        return  self.tipo
