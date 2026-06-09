from django.db import models
from apps.core.models import CustomUser
from apps.land.models import LandContract


# ======================================================
# TOWN
# ======================================================

class Town(models.Model):

    name            = models.CharField(max_length=200)
    name_urdu       = models.CharField(max_length=200, blank=True)
    land_contract   = models.ForeignKey(
                        LandContract,
                        on_delete=models.PROTECT,
                        related_name='towns',
                        null=True, blank=True
                      )
    location        = models.TextField(blank=True)
    total_area      = models.DecimalField(
                        max_digits=15,
                        decimal_places=2,
                        null=True, blank=True
                      )
    description     = models.TextField(blank=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return self.name

    @property
    def total_plots(self):
        return self.blocks.aggregate(
            total=models.Sum('plots__id')
        )['total'] or 0


# ======================================================
# BLOCK
# ======================================================

class Block(models.Model):

    town            = models.ForeignKey(
                        Town,
                        on_delete=models.CASCADE,
                        related_name='blocks'
                      )
    name            = models.CharField(max_length=100)
    name_urdu       = models.CharField(max_length=100, blank=True)
    total_plots     = models.PositiveIntegerField(default=0)
    description     = models.TextField(blank=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    def __str__(self):
        return f"{self.town.name} — Block {self.name}"

    @property
    def available_plots(self):
        return self.plots.filter(status='AVAILABLE', is_deleted=False).count()

    @property
    def sold_plots(self):
        return self.plots.filter(status='SOLD', is_deleted=False).count()


# ======================================================
# PLOT
# ======================================================

class Plot(models.Model):

    SIZE_UNIT_CHOICES = [
        ('MARLA', 'Marla'),
        ('KANAL', 'Kanal'),
        ('SQFT',  'Square Feet'),
    ]

    TYPE_CHOICES = [
        ('RESIDENTIAL', 'Residential'),
        ('COMMERCIAL',  'Commercial'),
        ('CORNER',      'Corner'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BOOKED',    'Booked'),
        ('SOLD',      'Sold'),
        ('HOLD',      'Hold'),
        ('CANCELLED', 'Cancelled'),
    ]

    block           = models.ForeignKey(
                        Block,
                        on_delete=models.CASCADE,
                        related_name='plots'
                      )
    plot_no         = models.CharField(max_length=50)
    size            = models.DecimalField(max_digits=10, decimal_places=2)
    size_unit       = models.CharField(
                        max_length=10,
                        choices=SIZE_UNIT_CHOICES,
                        default='MARLA'
                      )
    plot_type       = models.CharField(
                        max_length=15,
                        choices=TYPE_CHOICES,
                        default='RESIDENTIAL'
                      )
    price           = models.DecimalField(max_digits=15, decimal_places=2)
    status          = models.CharField(
                        max_length=15,
                        choices=STATUS_CHOICES,
                        default='AVAILABLE'
                      )
    notes           = models.TextField(blank=True)
    is_deleted      = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                      )

    class Meta:
        unique_together = ('block', 'plot_no')
        ordering        = ['block', 'plot_no']

    def __str__(self):
        return f"Plot {self.plot_no} — {self.block}"


# ======================================================
# TOWN MAP
# ======================================================

class TownMap(models.Model):

    MAP_TYPE_CHOICES = [
        ('IMAGE', 'Image (JPG/PNG)'),
        ('PDF',   'PDF'),
    ]

    town            = models.ForeignKey(
                        Town,
                        on_delete=models.CASCADE,
                        related_name='maps'
                      )
    block           = models.ForeignKey(
                        Block,
                        on_delete=models.CASCADE,
                        null=True, blank=True,
                        related_name='maps'
                      )
    title           = models.CharField(
                        max_length=200,
                        help_text='e.g. Master Plan, Block A Layout'
                      )
    map_type        = models.CharField(
                        max_length=10,
                        choices=MAP_TYPE_CHOICES,
                        default='IMAGE'
                      )
    map_file        = models.FileField(upload_to='maps/')
    display_order   = models.PositiveIntegerField(default=0)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='maps_created'
                      )

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        block_str = f' — {self.block.name}' if self.block else ' — Master Plan'
        return f'{self.town.name}{block_str} — {self.title}'

    @property
    def is_image(self):
        return self.map_type == 'IMAGE'

    @property
    def is_pdf(self):
        return self.map_type == 'PDF'


# ======================================================
# PLOT COORDINATE
# ======================================================

class PlotCoordinate(models.Model):

    town_map        = models.ForeignKey(
                        TownMap,
                        on_delete=models.CASCADE,
                        related_name='coordinates'
                      )
    plot            = models.ForeignKey(
                        Plot,
                        on_delete=models.CASCADE,
                        related_name='coordinates'
                      )
    # Polygon points as percentage-based coordinates (0-100)
    # Format: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    coordinates     = models.JSONField(default=list)
    created_at      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(
                        CustomUser,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='coordinates_created'
                      )

    class Meta:
        unique_together = ('town_map', 'plot')

    def __str__(self):
        return f'Plot {self.plot.plot_no} on {self.town_map.title}'