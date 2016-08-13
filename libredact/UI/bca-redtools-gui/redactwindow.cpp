#include "redactwindow.h"
#include "ui_redactwindow.h"

RedactWindow::RedactWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::RedactWindow)
{
    ui->setupUi(this);
}

RedactWindow::~RedactWindow()
{
    delete ui;
}
