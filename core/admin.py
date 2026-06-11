from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv

from .models import GameSession, Player, Order, Transaction, Profile


# ── Profile (Leaderboard) ──────────────────────────────────────
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'get_first_name', 'total_pnl', 'get_last_login')
    ordering = ('-total_pnl',)
    search_fields = ('user__username', 'user__email', 'user__first_name')
    actions = ['export_leaderboard_csv', 'export_all_participants_csv']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'Name'

    def get_last_login(self, obj):
        return obj.user.last_login
    get_last_login.short_description = 'Last Login'

    def export_leaderboard_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="leaderboard_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Rank', 'Name', 'Email', 'Username', 'Total PnL', 'Last Login'])
        profiles = Profile.objects.select_related('user').order_by('-total_pnl')
        for rank, p in enumerate(profiles, 1):
            writer.writerow([
                rank,
                p.user.first_name or p.user.username,
                p.user.email,
                p.user.username,
                p.total_pnl,
                p.user.last_login.strftime('%Y-%m-%d %H:%M') if p.user.last_login else 'Never',
            ])
        return response
    export_leaderboard_csv.short_description = '📥 Export Full Leaderboard (CSV)'

    def export_all_participants_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="participants_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Username', 'Total PnL', 'Date Joined', 'Last Login', 'Active'])
        for u in __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model().objects.all().order_by('first_name'):
            profile = Profile.objects.filter(user=u).first()
            writer.writerow([
                u.first_name or u.username,
                u.email,
                u.username,
                profile.total_pnl if profile else 0,
                u.date_joined.strftime('%Y-%m-%d'),
                u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else 'Never',
                'Yes' if u.is_active else 'No',
            ])
        return response
    export_all_participants_csv.short_description = '📥 Export All Participants (CSV)'


# ── GameSession ────────────────────────────────────────────────
@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'is_active', 'is_finished', 'current_round', 'player_count', 'created_at', 'finished_at')
    list_filter = ('is_active', 'is_finished')
    ordering = ('-created_at',)
    actions = ['export_game_results_csv']

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = 'Players'

    def export_game_results_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="game_results_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Room Code', 'Player Name', 'Email', 'Seat', 'Cash', 'Assets', 'True Value', 'Net PnL', 'Game Finished At'])
        for game in queryset:
            true_value = sum(game.hidden_array) if game.hidden_array else '?'
            for p in game.players.select_related('user').all():
                net_pnl = p.cash + ((p.asset_count - 3) * true_value) if game.is_finished else 'In Progress'
                writer.writerow([
                    game.room_code,
                    p.user.first_name or p.user.username,
                    p.user.email,
                    p.seat_number,
                    p.cash,
                    p.asset_count,
                    true_value,
                    net_pnl,
                    game.finished_at.strftime('%Y-%m-%d %H:%M') if game.finished_at else 'Not finished',
                ])
        return response
    export_game_results_csv.short_description = '📥 Export Game Results (CSV)'


# ── Player ─────────────────────────────────────────────────────
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'seat_number', 'cash', 'asset_count')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    list_filter = ('game__is_finished',)


# ── Order / Transaction ────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'order_type', 'price', 'round_number', 'is_active', 'created_at')
    list_filter = ('order_type', 'is_active')


admin.site.register(Transaction)

# ── Branding ───────────────────────────────────────────────────
admin.site.site_header = "QuantX Week 2 — Admin Panel"
admin.site.site_title = "QuantX Admin"
admin.site.index_title = "Quant Club IIT BHU — MarketSmith"
