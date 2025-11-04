import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'login_screen.dart';
import 'dashboard_screen.dart';

class AuthWrapper extends StatefulWidget {
  @override
  _AuthWrapperState createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    // Initialize auth state when app starts
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AuthProvider>().initialize();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        switch (authProvider.status) {
          case AuthStatus.loading:
          case AuthStatus.initial:
            return _LoadingScreen();

          case AuthStatus.authenticated:
            if (authProvider.user != null) {
              // Convert new User model to legacy Student format for compatibility
              final legacyStudent = {
                'id': authProvider.user!.id,
                'name': authProvider.user!.fullName,
                'email': authProvider.user!.email,
                'enrollment_status': 'Enrolled', // Default status
              };
              return DashboardScreen(student: legacyStudent);
            }
            return LoginScreen();

          case AuthStatus.unauthenticated:
          default:
            return LoginScreen();
        }
      },
    );
  }
}

class _LoadingScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset('assets/images/aada_logo_login.png', height: 120),
            SizedBox(height: 32),
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.amber),
            ),
            SizedBox(height: 16),
            Text(
              'ATLANTA ACADEMY OF DENTAL ASSISTING',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.amber,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 8),
            Text(
              'Loading...',
              style: TextStyle(
                fontSize: 14,
                color: theme.colorScheme.onBackground.withOpacity(0.7),
              ),
            ),
          ],
        ),
      ),
    );
  }
}