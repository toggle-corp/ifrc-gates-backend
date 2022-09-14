resource "aws_alb" "alb" {
  name           = "lb-${var.environment}"
  subnets        = aws_subnet.public.*.id
  security_groups = [aws_security_group.alb_sg.id]
}

resource "aws_alb_target_group" "tg" {
  name        = "target-group-${var.environment}"
  port        = 7020
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.vpc.id

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 20
    protocol            = "HTTP"
    matcher             = "200"
    path                = var.health_check_path
    interval            = 30
  }
}

# Redirecting all incomming traffic from ALB to the target group
resource "aws_alb_listener" "app_listener" {
  load_balancer_arn = aws_alb.alb.id
  port              = var.app_port
  protocol          = "HTTP"
  #ssl_policy        = "ELBSecurityPolicy-2016-08"
  #certificate_arn   = "arn:aws:iam::187416307283:server-certificate/test_cert_rab3wuqwgja25ct3n4jdj2tzu4"
  #enable above 2 if you are using HTTPS listner and change protocal from HTTPS to HTTPS
  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.tg.arn
  }
}