from django.contrib import admin
from django.http import HttpResponse
from django.db.models import Sum
from .models import GameSession, Player, Order, Transaction, Profile
import csv

admin.site.site_header  = "QuantX Week 2 — Admin Panel"
admin.site.site_title   = "QuantX Admin"
admin.site.index_title  = "Quant Club IIT BHU — MarketSmith"


def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [f.name for f in meta.fields]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f) for f in field_names])
    return response
export_as_csv.short_description = "Export selected as CSV"


def export_leaderboard_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=leaderboard.csv'
    writer = csv.writer(response)
    writer.writerow(['Rank', 'Name', 'Email', 'Total PnL'])
    profiles = Profile.objects.select_related('user').order_by('-total_pnl')
    for i, profile in enumerate(profiles, 1):
        writer.writerow([
            i,
            profile.user.first_name or profile.user.username,
            profile.user.username,
            profile.total_pnl
        ])
    return response
export_leaderboard_csv.short_description = "Export Full Leaderboard as CSV"


def export_game_results_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=game_results.csv'
    writer = csv.writer(response)
    writer.writerow([
        'Game ID', 'Room Code', 'Player Name', 'Email',
        'Seat', 'Cash', 'Assets', 'Hidden Array',
        'True Asset Value', 'Net PnL', 'Finished At'
    ])
    for game in queryset:
        true_value = sum(game.hidden_array) if game.hidden_array else 0
        for p in game.players.select_related('user').order_by('seat_number'):
            net_pnl = p.cash + ((p.asset_count - 3) * true_value)
            writer.writerow([
                game.id,
                game.room_code,
                p.user.first_name or p.user.username,
                p.user.username,
                p.seat_number,
                p.cash,
                p.asset_count,
                str(game.hidden_array),
                true_value,
                net_pnl,
                game.finished_at,
            ])
    return response
export_game_results_csv.short_description = "Export Game Results as CSV"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('get_name', 'get_email', 'total_pnl')
    search_fields = ('user__first_name', 'user__username')
    ordering      = ('-total_pnl',)
    actions       = [export_leaderboard_csv, export_as_csv]

    def get_name(self, obj):
        return obj.user.first_name or obj.user.username
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.username
    get_email.short_description = 'Email'


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display  = ('room_code', 'is_active', 'is_finished',
                     'current_round', 'get_player_count', 'get_true_value',
                     'get_questions', 'finished_at')
    list_filter   = ('is_active', 'is_finished')
    actions       = [export_game_results_csv, export_as_csv]

    def get_true_value(self, obj):
        return sum(obj.hidden_array) if obj.hidden_array else '-'
    get_true_value.short_description = 'True Value'

    def get_player_count(self, obj):
        return obj.players.count()
    get_player_count.short_description = 'Players'

    def get_questions(self, obj):
        if not obj.ques_list:
            return '-'
        return f"{len(obj.ques_list)} questions"
    get_questions.short_description = 'Questions'


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display  = ('get_name', 'get_email', 'game', 'seat_number',
                     'cash', 'asset_count')
    search_fields = ('user__first_name', 'user__username')
    list_filter   = ('game',)
    actions       = [export_as_csv]

    def get_name(self, obj):
        return obj.user.first_name or obj.user.username
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.username
    get_email.short_description = 'Email'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('player', 'game', 'order_type', 'price',
                     'round_number', 'is_active', 'created_at')
    list_filter   = ('order_type', 'is_active', 'game')
    actions       = [export_as_csv]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
