import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'quizzes_screen.dart';
import 'my_tuition_screen.dart';
import 'login_screen.dart';

class JobBoardScreen extends StatelessWidget {
  final Map<String, dynamic> student;
  JobBoardScreen({required this.student});

  void logout(BuildContext context) {
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => LoginScreen()),
      (route) => false,
    );
  }

  void navigateTo(BuildContext context, Widget screen) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text("Job Board"),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => logout(context),
          )
        ],
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              title: Text("Dental Assistant – Smile Dental"),
              subtitle: Text("Atlanta, GA"),
              trailing: ElevatedButton(
                onPressed: () {},
                child: Text("Apply"),
              ),
            ),
          ),
          Card(
            child: ListTile(
              title: Text("Sterilization Tech – Tooth & Co."),
              subtitle: Text("Marietta, GA"),
              trailing: ElevatedButton(
                onPressed: () {},
                child: Text("Apply"),
              ),
            ),
          ),
          Card(
            child: ListTile(
              title: Text("Front Desk Admin – Clear Dental"),
              subtitle: Text("Kennesaw, GA"),
              trailing: ElevatedButton(
                onPressed: () {},
                child: Text("Apply"),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 2,
        selectedItemColor: Colors.black,
        unselectedItemColor: Colors.grey,
        onTap: (index) {
          if (index == 0) navigateTo(context, DashboardScreen(student: student));
          if (index == 1) navigateTo(context, QuizzesScreen(student: student));
          if (index == 3) navigateTo(context, MyTuitionScreen(student: student));
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Dashboard"),
          BottomNavigationBarItem(icon: Icon(Icons.quiz), label: "Quizzes"),
          BottomNavigationBarItem(icon: Icon(Icons.work), label: "Job Board"),
          BottomNavigationBarItem(icon: Icon(Icons.attach_money), label: "My Tuition"),
        ],
      ),
    );
  }
}
