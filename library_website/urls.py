from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name="library_homePage"),
    path("returnBook", views.returnBook, name="library_returnBook"),
    path("extendReturn", views.extendReturn, name="library_extendReturn"),
    path("cancelReservation", views.cancelReservation, name="library_cancelReservation"),
    path("logout", views.logoutView, name="library_logout"),
    path('signUp', views.signUpPage, name="library_signUpPage"),
    path('memberLogIn', views.memberLogInPage, name="library_memberLogInPage"),
    path('bookDetails', views.bookDetailsPage, name="library_bookDetailsPage"),
    path('myAccount', views.myAccountPage, name="library_myAccountPage"),
    path('try', views.tryyy, name="library_myAccountPage"),
    path('visitorBookDetails', views.visitorBookDetailsPage, name="library_visitorBookDetailsPage"),
    path('adminLoginPage', views.adminLogInPage, name="library_adminLoginPage"),
    path('adminAccountPage', views.adminAccountPage, name="library_adminAccountPage"),
    path('adminBorrowPage', views.adminBorrowPage, name="library_adminAccountBorrowPage"),
    path('adminReservationPage', views.adminReservationPage, name="library_adminAccountReservationPage"),
    path('adminFinesPage', views.adminFinesPage, name="library_adminAccountFinesPage"),
    path('memberPayFinesPage', views.memberPayFinesPage, name="library_memberPayFinesPage"),
    path('memberFinesPaidPage', views.memberFinesPaidPage, name="library_memberFinesPaidPage"),
    path('reservedBookPage', views.reservedBookPage, name="library_reservedPage"),
    path('borrowBookPage', views.borrowBookPage, name="library_borrowPage"),
]