import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dashboard_screen.dart';
import '../api/api_service.dart';
import '../providers/auth_provider.dart';
import 'onboarding/registration_screen.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  bool isLoading = false;
  bool _useNewAuth = true; // Toggle between new JWT auth and legacy auth
  bool _obscurePassword = true;

  void login() async {
    final email = emailController.text.trim();

    if (_useNewAuth) {
      // New JWT authentication
      final password = passwordController.text;

      if (email.isEmpty || password.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Please enter email and password")),
        );
        return;
      }

      final authProvider = context.read<AuthProvider>();
      final success = await authProvider.login(email: email, password: password);

      if (!mounted) return; // Check if widget is still mounted

      if (!success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? "Login failed"),
            backgroundColor: Colors.red,
          ),
        );
      }
      // Navigation is handled by AuthWrapper
    } else {
      // Legacy authentication (for existing students)
      if (email.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Please enter your email")),
        );
        return;
      }

      setState(() {
        isLoading = true;
      });

      final student = await ApiService.login(email);

      setState(() {
        isLoading = false;
      });

      if (student != null) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => DashboardScreen(student: student),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Login failed. Student not found.")),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Image.asset('assets/images/aada_logo_login.png', height: 100),
              SizedBox(height: 24),
              Text(
                'ATLANTA ACADEMY OF DENTAL ASSISTING',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 12),
              Text(
                'Your Future as a Dental Assistant Begins Now',
                style: TextStyle(fontSize: 16, color: theme.colorScheme.onBackground),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 32),

              // Auth method toggle
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        onTap: () => setState(() => _useNewAuth = true),
                        child: Container(
                          padding: EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: _useNewAuth ? Colors.amber : Colors.transparent,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            'New Account',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontWeight: _useNewAuth ? FontWeight.w600 : FontWeight.normal,
                              color: _useNewAuth ? Colors.black : theme.colorScheme.onSurface,
                            ),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(width: 8),
                    Expanded(
                      child: GestureDetector(
                        onTap: () => setState(() => _useNewAuth = false),
                        child: Container(
                          padding: EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: !_useNewAuth ? Colors.amber : Colors.transparent,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            'Legacy Login',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontWeight: !_useNewAuth ? FontWeight.w600 : FontWeight.normal,
                              color: !_useNewAuth ? Colors.black : theme.colorScheme.onSurface,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(height: 24),

              TextField(
                controller: emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: InputDecoration(
                  labelText: 'Email',
                  prefixIcon: Icon(Icons.email_outlined),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),

              if (_useNewAuth) ...[
                SizedBox(height: 16),
                TextField(
                  controller: passwordController,
                  obscureText: _obscurePassword,
                  decoration: InputDecoration(
                    labelText: 'Password',
                    prefixIcon: Icon(Icons.lock_outlined),
                    suffixIcon: IconButton(
                      icon: Icon(_obscurePassword ? Icons.visibility : Icons.visibility_off),
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                    ),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ],

              SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                child: Consumer<AuthProvider>(
                  builder: (context, authProvider, child) {
                    final isAuthLoading = _useNewAuth && authProvider.isLoading;
                    return ElevatedButton(
                      onPressed: (isLoading || isAuthLoading) ? null : login,
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: Colors.amber,
                        foregroundColor: Colors.black,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: (isLoading || isAuthLoading)
                          ? CircularProgressIndicator(
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.black),
                            )
                          : Text('Log In', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                    );
                  },
                ),
              ),

              if (_useNewAuth) ...[
                SizedBox(height: 16),
                TextButton(
                  onPressed: () {
                    // TODO: Implement forgot password
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Forgot password feature coming soon')),
                    );
                  },
                  child: Text(
                    'Forgot Password?',
                    style: TextStyle(color: Colors.amber[700]),
                  ),
                ),
                SizedBox(height: 8),
                TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => RegistrationScreen()),
                    );
                  },
                  child: RichText(
                    text: TextSpan(
                      text: "Don't have an account? ",
                      style: TextStyle(color: theme.colorScheme.onBackground),
                      children: [
                        TextSpan(
                          text: "Sign Up",
                          style: TextStyle(
                            color: Colors.amber[700],
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
