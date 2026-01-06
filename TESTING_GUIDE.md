# Testing Guide

## Overview
This guide covers testing procedures for the EdTech backend application.

## Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test question_solver

# Run with coverage
coverage run manage.py test
coverage report
```

## Test Categories
- Unit tests for individual functions
- Integration tests for API endpoints
- End-to-end tests for complete workflows

## API Testing
Use the provided test scripts:
```bash
./test_deployed_api.sh
./test_comprehensive_api.py
```

## Manual Testing
Test the following endpoints manually:
- Health check: `GET /api/health/`
- Authentication: `/api/auth/`
- Quiz functionality: `/api/quiz/`
- Subscription management: `/api/subscription/`
- Payment processing: `/api/payment/`

## Performance Testing
- Load testing with multiple concurrent users
- Database query optimization
- API response time monitoring

## Security Testing
- Authentication and authorization checks
- Input validation testing
- SQL injection prevention
- XSS protection verification