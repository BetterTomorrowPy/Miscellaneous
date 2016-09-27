# -*- coding: utf-8 -*-
""""""
from django.views.generic import View
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest, Http404


class JsonResponseMixin(object):
    """json mixin"""

    def render_to_response(self, context=None):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **http_response_kwargs):
        return HttpResponse(content,
                            content_type='application/json',
                            **http_response_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)



class FieldHandler(View):
    """
        Us:
            import re

            p = re.search(r'^fields/(?P<field_id>\d*)', 'fields/[None or field_id]')
            field_id = p.group(1)
    """

    def get(self, request, field_id=None):
        """Get field for given id or show name."""
        # _id = request.GET.get('field_id')
        _name = request.GET.get('show_name')
        if field_id:
            pfs = ProfileField.objects.filter(pk=field_id)
        elif _name:
            pfs = ProfileField.objects.filter(show_name=_name)
        else:
            raise HttpResponseBadRequest
        if pfs:
            return JsonResponse(data={
                'field_info': pfs.values(),
            })
        raise Http404

    def post(self, request):
        """Create field."""
        show_name = request.POST.get('show_name')
        description = request.POST.get('description')
        field_type = request.POST.get('type')
        field_value = request.POST.get('reserve')

        if show_name and field_type:
            p = ProfileField.objects.filter(Q(show_name=show_name) & Q(is_delete=0))
            if not p:
                nf = ProfileField(
                    show_name=show_name, 
                    type=field_type, 
                    description=description, 
                    field_value=field_value, 
                    )
                nf.save()
                nf.name = 'new_field_name' + str(nf.id)
                nf.save()
                return JsonResponse(nf.to_dict())
            return JsonResponse({
                'code': -1, 
                'msg': 'field is exsits.'
                })
        return HttpResponseBadRequest

    def put(self, request):
        pass

    def delete(self, request, field_id=None):
        """"""
        if not field_id:
            raise HttpResponseBadRequest('Error field_id.')
        p = get_object_or_404(ProfileField, pk=field_id, is_delete=0, is_inner=0)
        p.is_delete = 1
        p.save()
        return JsonResponse(
                {
                    'code': 0, 
                    'msg': 'delete success'
                }
            )


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'], 
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user