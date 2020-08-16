from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect,
                   request,
                   Response,
                   send_file
                   )
from flask_login import current_user

from sadhu.web import acl, forms
from sadhu import models

import datetime
import csv
import io

module = Blueprint('administration.classes',
                   __name__,
                   url_prefix='/classes',
                   )


@module.route('/')
@acl.allows.requires(acl.is_lecturer)
def index():
    classes = models.Class.objects(
            owner=current_user._get_current_object()).order_by('-id')
    return render_template('/administration/classes/index.html',
                           classes=classes)


@module.route('/<class_id>/edit', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_class_owner)
def edit(class_id):
    courses = models.Course.objects()

    class_ = models.Class.objects.get(id=class_id)
    form = forms.classes.ClassForm(obj=class_)
    # le_form = forms.classes.LimitedEnrollmentForm(
    #         obj=class_.limited_enrollment)

    # form.limited_enrollment = le_form
    course_choices = [(str(c.id), c.name) for c in courses]
    form.course.choices = course_choices
    if request.method == 'GET':
        form.course.data = str(class_.course.id)
    method_choices = [('email', 'Email'), ('student_id', 'Student ID')]
    form.limited_enrollment.method.choices = method_choices

    if not form.validate_on_submit():
        return render_template('/administration/classes/create-edit.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')

    form.populate_obj(class_)
    course = models.Course.objects.get(id=form.course.data)
    class_.course = course
    class_.save()
    return redirect(url_for('administration.classes.index'))


@module.route('/<class_id>/delete')
@acl.allows.requires(acl.is_class_owner)
def delete(class_id):

    class_ = models.Class.objects.get(id=class_id)
    class_.delete()
    return redirect(url_for('administration.classes.index'))


@module.route('/create', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_lecturer)
def create():
    form = forms.classes.ClassForm()
    courses = models.Course.objects()

    course_choices = [(str(c.id), c.name) for c in courses]
    form.course.choices = course_choices
    method_choices = [('email', 'Email'), ('student_id', 'Student ID')]
    form.limited_enrollment.method.choices = method_choices

    if not form.validate_on_submit():
        return render_template('/administration/classes/create-edit.html',
                               form=form)
    data = form.data.copy()
    data.pop('csrf_token')
    # data.pop('limited_enrollment')

    class_ = models.Class(**data)
    course = models.Course.objects.get(id=form.course.data)
    class_.course = course
    class_.owner = current_user._get_current_object()
    class_.save()
    return redirect(url_for('administration.classes.index'))


@module.route('/<class_id>')
@acl.allows.requires(acl.is_class_owner)
def view(class_id):
    class_ = models.Class.objects.get(id=class_id)
    return render_template('/administration/classes/view.html',
                           class_=class_)


@module.route('/<class_id>/set-assignment-time/<assignment_id>',
              methods=['GET', 'POST'])
@acl.allows.requires(acl.is_class_owner)
def set_assignment_time(class_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    ass_time = class_.get_assignment_schedule(assignment)

    form = forms.assignments.AssignmentTimeForm(obj=ass_time)

    if not form.validate_on_submit():
        return render_template(
            '/administration/classes/set-assignment-time.html',
            form=form,
            assignment=assignment)
    if not ass_time:
        ass_time = models.AssignmentTime(assignment=assignment)

    ass_time.started_date = form.started_date.data
    ass_time.ended_date = form.ended_date.data

    if ass_time not in class_.assignment_schedule:
        class_.assignment_schedule.append(ass_time)
    class_.save()

    return redirect(url_for('administration.classes.view', class_id=class_id))


@module.route('/<class_id>/users')
@acl.allows.requires(acl.is_class_owner)
def list_students(class_id):
    class_ = models.Class.objects.get(id=class_id)
    enrollments = class_.get_enrollments()
    enrollments = sorted(enrollments,
                         key=lambda e: e.user.first_name)

    unenrollments = []
    never_login = []
    le = class_.limited_enrollment
    for grantee in le.grantees:
        if le.method == 'email':
            user = models.User.objects(email=grantee).first()
        elif le.method == 'student_id':
            user = models.User.objects(username=grantee).first()

        if user is None:
            never_login.append(grantee)
            continue

        if not class_.is_enrolled(user=user):
            unenrollments.append(user)


    return render_template('/administration/classes/list-users.html',
                           class_=class_,
                           enrollments=enrollments,
                           unenrollments=unenrollments,
                           never_login=never_login)


@module.route('/<class_id>/users/<user_id>')
@acl.allows.requires(acl.is_class_owner)
def show_user_score(class_id, user_id):
    class_ = models.Class.objects.get(id=class_id)
    user = models.User.objects.get(id=user_id)
    assignments = class_.course.assignments

    return render_template('/administration/classes/show-user-score.html',
                           class_=class_,
                           user=user,
                           assignments=assignments)


@module.route('/<class_id>/users/<user_id>/assignments/<assignment_id>')
@acl.allows.requires(acl.is_class_owner)
def show_user_assignment(class_id, user_id, assignment_id):
    class_ = models.Class.objects.get(id=class_id)
    user = models.User.objects.get(id=user_id)
    assignment = models.Assignment.objects.get(id=assignment_id)

    return render_template(
            '/administration/classes/show-user-assignment.html',
            class_=class_,
            user=user,
            assignment=assignment)


# @module.route('/<class_id>/assignments/<assignment_id>/users')
# @acl.allows.requires(acl.is_class_owner)
# def list_assignment_users(class_id, assignment_id):
#     class_ = models.Class.objects.get(id=class_id)
#     assignment = models.Assignment.objects.get(id=assignment_id)

#     return render_template(
#             '/administration/classes/show-user-assignment.html',
#             class_=class_,
#             user=user,
#             assignment=assignment)


@module.route('/<class_id>/users/export-attendents')
@acl.allows.requires(acl.is_class_owner)
def export_attendants(class_id):
    class_ = models.Class.objects.get(id=class_id)
    enrollments = models.Enrollment.objects(enrolled_class=class_)
    users = [e.user for e in enrollments]
    users.sort(key=lambda u: u.username)


    assignments = []
    for ass_time in class_.assignment_schedule:
        assignments.append(ass_time.assignment)

    assignments.sort(key=lambda ass: ass.name)
    header = ['id']
    subheader = ['no']

    for ass in assignments:
        header.append(ass.name)
        subheader.append(len(ass.challenges))

    output =  io.StringIO()
    writer = csv.writer(output)

    writer.writerow(header)
    writer.writerow(subheader)
    for user in users:
        data = [user.username]
        for ass in assignments:
            challenges = ass.check_user_submission(class_, user)
            data.append(len(challenges))
        writer.writerow(data)

    return Response(output.getvalue(),
                    mimetype='text/csv',
                    headers={
                        'Content-disposition':
                        f'attachment; filename={class_.id}-attendants.csv'
    				})


@module.route('/<class_id>/users/export-scores')
@acl.allows.requires(acl.is_class_owner)
def export_scores(class_id):
    class_ = models.Class.objects.get(id=class_id)
    enrollments = models.Enrollment.objects(enrolled_class=class_)
    users = [e.user for e in enrollments]
    users.sort(key=lambda u: u.username)


    assignments = []
    for ass_time in class_.assignment_schedule:
        assignments.append(ass_time.assignment)

    assignments.sort(key=lambda ass: ass.name)
    header = ['id']
    subheader = ['no']

    total_score = 0
    for ass in assignments:
        header.append(ass.name)
        subheader.append(ass.score)
        total_score += ass.score
    header.append('total')
    subheader.append(total_score)

    output =  io.StringIO()
    writer = csv.writer(output)

    writer.writerow(header)
    writer.writerow(subheader)
    for user in users:
        total_score = 0
        data = [user.username]
        for ass in assignments:
            score = ass.get_score(class_, user)
            data.append(score)
            total_score += score
        data.append(total_score)
        writer.writerow(data)

    return Response(output.getvalue(),
                    mimetype='text/csv',
                    headers={
                        'Content-disposition':
                        f'attachment; filename={class_.id}-scores.csv'
    				})


@module.route('/<class_id>/add-user/<user_id>')
@acl.allows.requires(acl.is_class_owner)
def add_user_to_class(class_id, user_id):
    class_ = models.Class.objects.get(id=class_id)
    user = models.User.objects.get(id=user_id)

    user.enroll(class_)
    return redirect(request.referrer)



@module.route('/<class_id>/teaching-assistants/add', methods=['GET', 'POST'])
@acl.allows.requires(acl.is_class_owner)
def add_teaching_assistant(class_id):
    class_ = models.Class.objects().get(id=class_id)
    users = models.User.objects().order_by('first_name')

    form = forms.classes.TeachingAssistantAddingForm()
    form.users.choices = [(str(user.id),
                           '{} {} ({}, {})'.format(
                               user.first_name,
                               user.last_name,
                               user.username,
                               user.email)) for user in users]

    if not form.validate_on_submit():
        return render_template(
                '/administration/classes/add-teaching-assistant.html',
                form=form,
                class_=class_,
                users=users)

    for user_id in form.users.data:
        user = models.User.objects.get(id=user_id)

        found_user = False
        for ta in class_.teaching_assistants:
            if ta.user == user:
                found_user = True
                break

        if not found_user:
            ta = models.TeachingAssistant(
                    user=user,
                    ended_date=class_.ended_date
                    )
            class_.teaching_assistants.append(ta)
    class_.save()

    return redirect(url_for('administration.classes.view', class_id=class_id))
