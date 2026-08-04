import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'

// Every view is route-level code-split (dynamic import) instead of statically
// imported here. Statically importing ~25 views meant the Login screen — the
// very first thing an unauthenticated visitor sees — couldn't render until
// the ENTIRE app (every view for every page) had downloaded as one ~590kB
// bundle. On a slow/real mobile connection that's 15s+ of a blank/unresponsive
// page before Sign In even works, which reads as "sign in hangs, need to
// refresh". Each view now ships as its own small chunk, fetched only when
// actually navigated to.
const Login = () => import('./views/Login.vue')
const Locations = () => import('./views/Locations.vue')
const Vehicles = () => import('./views/Vehicles.vue')
const VehicleDetail = () => import('./views/VehicleDetail.vue')
const FuelVehicles = () => import('./views/FuelVehicles.vue')
const FuelDetail = () => import('./views/FuelDetail.vue')
const Pilots = () => import('./views/Pilots.vue')
const PilotDetail = () => import('./views/PilotDetail.vue')
const Alerts = () => import('./views/Alerts.vue')
const Geofences = () => import('./views/Geofences.vue')

// New sidebar-group pages (preview / mock data — see src/mock.js). No
// dedicated backend endpoints exist for these yet, so they render
// deterministic seeded mock data following the same visual conventions as
// the pages above.
const FleetOverview = () => import('./views/FleetOverview.vue')
const VehicleDocuments = () => import('./views/VehicleDocuments.vue')
const RouteHistory = () => import('./views/RouteHistory.vue')
const FuelReports = () => import('./views/FuelReports.vue')
const FuelEfficiency = () => import('./views/FuelEfficiency.vue')
const PilotAttendance = () => import('./views/PilotAttendance.vue')
const PilotPerformance = () => import('./views/PilotPerformance.vue')
const PilotSalary = () => import('./views/PilotSalary.vue')
const TripPlanner = () => import('./views/TripPlanner.vue')
const TripEta = () => import('./views/TripEta.vue')
const BillingOrders = () => import('./views/BillingOrders.vue')
const BillingInvoices = () => import('./views/BillingInvoices.vue')
const BillingExpenses = () => import('./views/BillingExpenses.vue')
const AiPredictions = () => import('./views/AiPredictions.vue')
const AiRouteOptimization = () => import('./views/AiRouteOptimization.vue')

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/fleet-overview' }, // Fleet Overview: first item of the first sidebar group
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
  if (to.path === '/login' && auth.isAuthed) return '/'
})

export default router
