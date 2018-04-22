from django.contrib import admin
from comum.models import *
# Register your models here.

def encerrar_partida(modeladmin, request, queryset):
    if request.user.is_superuser:
        for jogo in queryset:
            jogo.finalizar()
encerrar_partida.short_description = "Finalizar Partida"


def encerrar_rodada(modeladmin, request, queryset):
    for rodada in queryset:
        rodada.finalizar()
encerrar_rodada.short_description = "Finalizar Rodada"


class ApostaBilheteInline(admin.TabularInline):
    model = Aposta
    fields = (
        'jogo',
        'tipo',
        'bilhete',
    )
    extra = 1


class JogoRodadaInline(admin.TabularInline):
    model = Jogo

    fields = (
        ('time_casa',
        'time_fora',),
        'campeonato',
        'data',
    )

    readonly_fields = (
        'status',
        'valor_total_apostado',
    )

    extra = 1


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'local',)


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'local',
    )


@admin.register(Bilhete)
class BilheteAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'valor',
        'premio',
        'premiado',
        'usuario',
        'total_apostas',
    )

    fieldsets = (
        ("", {
            'fields': ('valor', 'usuario',),
        }),
    )

    readonly_fields = (
        'premio',
        'premiado',
    )

    inlines = (ApostaBilheteInline,)


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'resultado',
        'campeonato',
        'status',
        'valor_total_apostado',
    )

    readonly_fields = (
        'status',
        'valor_total_apostado',
    )

    actions = [encerrar_partida]

@admin.register(Rodada)
class RodadaAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
    )

    inlines = (JogoRodadaInline,)

    actions = [encerrar_rodada]