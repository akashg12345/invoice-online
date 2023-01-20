# Third Party imports
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import requests
# Local Applications imports
from invoice.models.customer import Customer
from invoice.models.inv import Invoice
from invoice.forms import CustomerForm


@login_required(login_url='users:login')
def customer_list(request):
    """List all Customers

    List all customers and paginate them to display 25
    customers per page.

    """
    customer = Customer.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(customer, 25)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    context = {
        'title': 'Customer List',
        'customers': customers,
    }
    return render(request, 'invoice/customers.html', context)


@login_required(login_url='users:login')
def customer(request, customer_id):
    """
      Displays the details for a particular customer with their
      invocies.

    """
    customer = get_object_or_404(Customer, pk=customer_id)
    invoices = Invoice.objects.filter(customer=customer).order_by('-date_created')
    context = {
        'title': "Customer info - %s" % customer.name,
        'customer': customer,
        'invoices': invoices,
    }
    return render(request, 'invoice/customer.html', context)

def send_simple_message():
	return requests.post(
		"https://api.mailgun.net/v3/sandboxa712d3ffed70485d992d5e4b72756a08.mailgun.org/messages",
		auth=("api", "d9cca0779272ab83b19cc503b1151e42-f7d687c0-748d3c9c"),
		data={"from": "Mailgun Sandbox <postmaster@sandboxa712d3ffed70485d992d5e4b72756a08.mailgun.org>",
			"to": "akash <akash.gautam29@gmail.com>",
			"subject": "Hello akash",
			"text": "Congratulations akash, you just sent an email with Mailgun!  You are truly awesome!"})
# View for creating a new customer.
@login_required(login_url='users:login')
def new_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Customer created successfully')
            return redirect('invoice:customer_list')
    else:
        form = CustomerForm()

    context = {'form': form}
    template_name = 'invoice/new_customer.html'
    send_simple_message()
    return render(request, template_name, context)


# Update customer
@login_required(login_url='users:login')
def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer details updated successfully')
            return HttpResponseRedirect(reverse('invoice:customer',
                                                args=(customer.id,)))
    else:
        form = CustomerForm(instance=customer)
    context = {
        'form': form,
    }
    template_name = 'invoice/customer.html'
    return render(request, template_name, context)


# Delete customer
@login_required(login_url='users:login')
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.delete()
    messages.success(request, "Customer successfully deleted.")
    return HttpResponseRedirect(reverse('invoice:customer_list'))
