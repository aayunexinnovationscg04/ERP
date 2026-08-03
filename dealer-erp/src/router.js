import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'

import Login from './views/Login.vue'
import Locations from './views/Locations.vue'
import Vehicles from './views/Vehicles.vue'
import VehicleDetail from './views/VehicleDetail.vue'
import FuelVehicles from './views/FuelVehicles.vue'
import FuelDetail from './views/FuelDetail.vue'
import Pilots from './views/Pilots.vue'
import PilotDetail from './views/PilotDetail.vue'
import Alerts from './views/Alerts.vue'
import Geofences from './views/Geofences.vue'

// New sidebar-group pages (preview / mock data — see src/mock.js). No
// dedicated backend endpoints exist for these yet, so they render
// deterministic seeded mock data following the same visual conventions as
// the pages above.
import FleetOverview from './views/FleetOverview.vue'
import VehicleDocuments from './views/VehicleDocuments.vue'
import RouteHistory from './views/RouteHistory.vue'
import FuelReports from './views/FuelReports.vue'
import FuelEfficiency from './views/FuelEfficiency.vue'
import PilotAttendance from './views/PilotAttendance.vue'
import PilotPerformance from './views/PilotPerformance.vue'
import PilotSalary from './views/PilotSalary.vue'
import TripPlanner from './views/TripPlanner.vue'
import TripEta from './views/TripEta.vue'
import BillingOrders from './views/BillingOrders.vue'
import BillingInvoices from './views/BillingInvoices.vue'
import BillingExpenses from './views/BillingExpenses.vue'
import AiPredictions from './views/AiPredictions.vue'
import AiRouteOptimization from './views/AiRouteOptimization.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/vehicles' }, // Vehicles is the default landing tab
  { path: '/locations', component: Locations },
  { path: '/vehicles', component: Vehicles },
  { path: '/vehicles/:id', component: VehicleDetail, props: true },
  { path: '/vehicle-documents', component: VehicleDocuments },
  { path: '/fleet-overview', component: FleetOverview },
  { path: '/route-history', component: RouteHistory },
  { path: '/fuel', component: FuelVehicles },
  { path: '/fuel/:id', component: FuelDetail, props: true },
  { path: '/fuel-reports', component: FuelReports },
  { path: '/fuel-efficiency', component: FuelEfficiency },
  { path: '/pilots', component: Pilots },
  { path: '/pilots/:id', component: PilotDetail, props: true },
  { path: '/pilot-attendance', component: PilotAttendance },
  { path: '/pilot-performance', component: PilotPerformance },
  { path: '/pilot-salary', component: PilotSalary },
  { path: '/trip-planner', component: TripPlanner },
  { path: '/trip-eta', component: TripEta },
  { path: '/alerts', component: Alerts },
  { path: '/geofences', component: Geofences },
  { path: '/billing-orders', component: BillingOrders },
  { path: '/billing-invoices', component: BillingInvoices },
  { path: '/billing-expenses', component: BillingExpenses },
  { path: '/ai-predictions', component: AiPredictions },
  { path: '/ai-route-optimization', component: AiRouteOptimization },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/vehicles'
})

export default router
