from jet.dashboard.modules import DashboardModule
from contact.models import Ticket

class RecentTickets(DashboardModule):
    title = 'Recent tickets'
    title_url = Ticket.get_admin_changelist_url()
    template = 'contact/dashboard_modules/recent_tickets.html'
    limit = 10

    def init_with_context(self, context):
        self.children = Ticket.objects.order_by('-date_add')[:self.limit]